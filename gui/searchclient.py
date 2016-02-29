import logging
import os
from Tkinter import *
import ttk
import ConfigParser

import analysis.typeahead as typeahead
import search.semantic_query as semantic
import indexfiles.loader
import search.proximity_finder as proximity


class AutoCompleteEntry(ttk.Entry):
    """

    """
    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self.topics_typeahead_list = None
        self.scroll = None

        if len(args) > 0:
            self.parent = args[0]

        # Listbox length
        if 'listboxLength' in kwargs:
            self.listboxLength = kwargs['listboxLength']
            del kwargs['listboxLength']
        else:
            self.listboxLength = 8

        Entry.__init__(self, *args, **kwargs)
        self.focus()

        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Return>", self.selection)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)

        self.listboxUp = False
        self.list_frame = ttk.Frame()
        empty_frame = ttk.Frame(self.list_frame)  # Necessary to force the window manager to redraw the widget
        empty_frame.grid()

    # noinspection PyUnusedLocal
    def changed(self, name, index, mode):
        """

        :param name:
        :param index:
        :param mode:
        :return:
        """
        if self.var.get() == '':
            if self.listboxUp:
                self.logger.debug('empty search, hide the list !!!')
                self.topics_typeahead_list.destroy()
                self.scroll.destroy()
                self.listboxUp = False
        else:
            topics = self.get_matching_topics()
            self.logger.debug('words found: %s', topics)
            if topics:
                self.logger.debug('self.listboxUp ? %s', self.listboxUp)
                self.list_frame.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                if not self.listboxUp:
                    self.topics_typeahead_list = ttk.Treeview(self.list_frame,
                                                              height=self.listboxLength,
                                                              columns=('id', 'lbl_en', 'lbl_fr'),
                                                              displaycolumns=0,
                                                              style='TopicsList.Treeview')
                    self.topics_typeahead_list.column(0, width=60)
                    self.topics_typeahead_list.bind("<Button-1>", self.selection)
                    self.topics_typeahead_list.bind("<Right>", self.selection)
                    self.topics_typeahead_list.grid(row=0, column=0)
                    self.scroll = ttk.Scrollbar(self.list_frame, orient=VERTICAL,
                                                command=self.topics_typeahead_list.yview)
                    self.topics_typeahead_list['yscrollcommand'] = self.scroll.set
                    self.scroll.grid(row=0, column=1, sticky=(N, S))
                    self.listboxUp = True

                for topic in self.topics_typeahead_list.get_children():
                    self.topics_typeahead_list.delete(topic)
                for topic in topics:
                    self.topics_typeahead_list.insert('', END, text=topic[1], values=(topic[0], topic[1], topic[2]))

            else:
                if self.listboxUp:
                    self.topics_typeahead_list.destroy()
                    self.scroll.destroy()
                    self.listboxUp = False

    def get_matching_topics(self):
        """

        :return:
        """
        self.logger.debug('looking up matching labels for: %s', self.var.get())
        self.logger.debug('nb matches found: %s', len(typeahead_index[self.var.get()]))
        return typeahead_index[self.var.get()]

    # noinspection PyUnusedLocal
    def selection(self, event):
        """

        :param event:
        :return:
        """
        if self.listboxUp:
            selected_index = self.topics_typeahead_list.selection()
            selected_item = self.topics_typeahead_list.item(selected_index)
            values = selected_item['values']
            self.logger.debug('Selection: %s', values[0])
            self.var.set('')

            topics_list.insert('', END, text=values[1], values=(values[0], values[1], values[2]))
            topics_list.selection_set(topics_list.get_children()[0])

            self.topics_typeahead_list.destroy()
            self.scroll.destroy()
            self.logger.debug('redraw topics list...3')
            self.listboxUp = False
            self.icursor(END)
            search_documents_by_topics()

    # noinspection PyUnusedLocal
    def move_up(self, event):
        """

        :param event:
        :return:
        """
        if self.listboxUp:
            focused = self.topics_typeahead_list.focus()

            if focused == '':
                self.logger.debug('focused is None, set focused to %s', self.topics_typeahead_list.get_children()[0])
                focused = self.topics_typeahead_list.get_children()[0]
                self.topics_typeahead_list.see(focused)  # Scroll!
                self.topics_typeahead_list.selection_set(focused)
                self.topics_typeahead_list.focus(focused)
            else:
                self.logger.debug('focused is not None, set focused to %s', self.topics_typeahead_list.next(focused))
                previous_item = self.topics_typeahead_list.prev(focused)
                self.topics_typeahead_list.see(previous_item)  # Scroll!
                self.topics_typeahead_list.selection_set(previous_item)
                self.topics_typeahead_list.focus(previous_item)

    # noinspection PyUnusedLocal
    def move_down(self, event):
        """

        :param event:
        :return:
        """
        if self.listboxUp:
            focused = self.topics_typeahead_list.focus()

            if focused == '':
                self.logger.debug('focused is None, set focused to %s', self.topics_typeahead_list.get_children()[0])
                focused = self.topics_typeahead_list.get_children()[0]
                self.topics_typeahead_list.see(focused)  # Scroll!
                self.topics_typeahead_list.selection_set(focused)
                self.topics_typeahead_list.focus(focused)
            else:
                self.logger.debug('focused is not None, set focused to %s', self.topics_typeahead_list.next(focused))
                next_item = self.topics_typeahead_list.next(focused)
                self.topics_typeahead_list.see(next_item)  # Scroll!
                self.topics_typeahead_list.selection_set(next_item)
                self.topics_typeahead_list.focus(next_item)


def search_documents_by_topics():
    """

    :return:
    """
    topics_ids = [str(topics_list.item(topic_id)['values'][0]) for topic_id in topics_list.get_children()]
    logging.getLogger(__name__).info('Searching documents for topics: %s', topics_ids)

    matching_documents, matching_topics = processor.execute(topics_ids, order_by_relevance=True)
    logging.getLogger(__name__).debug('Found documents for topics: %s', matching_documents)
    logging.getLogger(__name__).debug('Found topics: %s', matching_topics)

    for result in results_list.get_children():
        results_list.delete(result)
    for document in matching_documents:
        results_list.insert('', END, text=document)
    results_list.selection_set(results_list.get_children()[0])

    global typeahead_index
    typeahead_index = typeahead.IndexBuilder().build(topics_index=build_topics_index(matching_topics))
    global semantic_signature_text
    semantic_signature_text.delete('1.0', END)
    semantic_signature_text.insert('1.0', get_search_results_details(len(matching_documents), len(matching_topics)))


def get_search_results_details(nb_documents, nb_topics):
    """

    :param nb_documents:
    :param nb_topics:
    :return:
    """
    result = 'Details:'
    result += '\n- Nb documents found: {nb_doc}'.format(nb_doc=nb_documents)
    result += '\n- Nb relevant topics found: {nb_topics}'.format(nb_topics=nb_topics)
    return result


def build_topics_index(matching_topics):
    """

    :param matching_topics:
    :return:
    """
    result = dict()
    logging.getLogger(__name__).debug('Begin build_topics_index')
    for uri in matching_topics:
        if uri not in result:
            result[uri] = topics_index.index[str(uri)]

    logging.getLogger(__name__).debug('result: %s', result)

    return result


# noinspection PyUnusedLocal
def topic_selected(event):
    """

    :param event:
    :return:
    """
    logging.getLogger(__name__).debug('Fire event: topic selected')
    selected_index = topics_list.selection()
    selected_item = topics_list.item(selected_index)
    logging.getLogger().debug('Selected index: %s - selection: %s', selected_index, selected_item)
    topic_id = selected_item['values'][0]
    logging.getLogger().debug('Selection: %s', topic_id)
    topics_list.delete(selected_index)
    if len(topics_list.get_children()) > 0:
        search_documents_by_topics()
    else:
        reset_gui()


# noinspection PyUnusedLocal
def result_selected(event):
    """

    :param event:
    :return:
    """
    logging.getLogger(__name__).debug('Fire event: result selected')
    selected_index = results_list.selection()
    selected_item = results_list.item(selected_index)
    logging.getLogger().debug('Selection: %s', selected_item)
    target_file = selected_item['text']
    logging.getLogger().debug('Selection: %s', target_file)
    semantic_signature = files_index.get_enrichment_for_files(target_file)
    logging.getLogger().debug('Semantic signature: %s', semantic_signature)

    required_topics = get_list_selected_topics()
    hrt_match_number = 0  # minimum number of highly relevant terms matching
    results = finder.build_proximity_results(semantic_signature=semantic_signature,
                                             minimum_hrt_match_number=hrt_match_number,
                                             sort_criteria=proximity.SortBy.PROXIMITY_SCORE,
                                             required_topics=required_topics,
                                             ignored_files=[target_file]).proximity_results
    update_proximity_results(results, semantic_signature, target_file)
    update_semantic_signature_text(semantic_signature)


def get_list_selected_topics():
    """Retrieve the list of topics currently selected by the user.

    :return:
    """
    return [str(topics_list.item(topic_id)['values'][0]) for topic_id in topics_list.get_children()]


def update_proximity_results(results, semantic_signature, target_file):
    """Change text area 'Proximmity Result' according to the files in results
    and the semantic signature of the target file.

    :param results:
    :param semantic_signature:
    :param target_file:
    :return:
    """
    global proximity_results
    proximity_results.delete('1.0', END)

    proximity_results.tag_configure('highlight_result', font='"Deja Vu Sans Mono" 12 bold')
    proximity_results.insert('1.0', 'Found {nb} files "related" to file {file}s\n'.format(nb=len(results),
                                                                                          file=target_file))
    for i in range(len(results) if len(results) < 20 else 20):
        proximity_results.insert(END, '--------------------------------------------------\n')
        proximity_results.insert(END, ('File: {file} - Proximity score: {score}% '
                                       '- Nb matches: {nb}\n').format(file=results[i][0],
                                                                      score=proximity.get_total_proximity_score(results[i][1],
                                                                                                                semantic_signature),
                                                                      nb=len(results[i][1])))
        proximity_results.insert(END, '--------------------------------------------------\n')
        for topic_lbl, score in [(topic_lbl, score) for _, topic_lbl, _, score in results[i][1]]:
            if score == 10000:
                proximity_results.insert(END, '\t- {topic}: {score}\n'.format(topic=topic_lbl, score=score),
                                         'highlight_result')
            else:
                proximity_results.insert(END, '\t- {topic}: {score}\n'.format(topic=topic_lbl, score=score))


def update_semantic_signature_text(semantic_signature):
    """

    :param semantic_signature:
    :return:
    """
    global semantic_signature_text
    semantic_signature_text.tag_configure('highlight_result', font='"Deja Vu Sans Mono" 12 bold')
    semantic_signature_text.delete('1.0', END)

    semantic_signature_text.insert('1.0', 'Topic \t\t(Relevance):')
    for topic_id, relevance in semantic_signature:
        if relevance == 'H':
            semantic_signature_text.insert(END, '\n-{topic_lbl_en} \t\t({relevance})'
                                           .format(topic_lbl_en=get_topic_label(topic_id), relevance=relevance),
                                           'highlight_result')
        else:
            semantic_signature_text.insert(END, '\n-{topic_lbl_en} \t\t({relevance})'
                                           .format(topic_lbl_en=get_topic_label(topic_id), relevance=relevance))


def get_topic_label(topic_id):
    """

    :param topic_id:
    :return:
    """
    return topics_index.get_labels_for_topic_id(topic_id)[0]


def reset_gui():
    """
    Reset all elements of GUI to default values
    :return:
    """
    logging.getLogger(__name__).info('Resetting interface....')
    # Delete proximity results
    global proximity_results
    proximity_results.delete('1.0', END)
    # Delete semantic signature
    global semantic_signature_text
    semantic_signature_text.delete('1.0', END)
    # Delete results list
    for result in results_list.get_children():
        results_list.delete(result)
    # Delete selected topics list
    for topic in topics_list.get_children():
        topics_list.delete(topic)
    # Reset topics labels index
    global typeahead_index
    global typeahead_index_full
    typeahead_index = typeahead_index_full


# if __name__ == '__main__':
# Get configuration parameters
basedir = os.path.abspath(os.path.dirname(__file__))
config = ConfigParser.SafeConfigParser()
# config.read(os.path.join(basedir, 'search_client.conf'))
config.read(os.path.join(basedir, 'search_client_test.conf'))

# Set appropriate logging level
numeric_level = getattr(logging, config.get('LOGGING', 'level').upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % config.get('LOGGING', 'level'))
logging.basicConfig(level=numeric_level, format='%(name)s - %(levelname)s - %(message)s')

# Load all various indexes used throughout the application
index_folder = config.get('INDEX', 'index_dir')
files_index_filename = config.get('INDEX', 'files_index_filename')
files_dates_index_filename = config.get('INDEX', 'files_dates_index_filename')
topics_index_filename = config.get('INDEX', 'topics_index_filename')
topics_occurrences_index_filename = config.get('INDEX', 'topics_occurrences_index_filename')
topics_labels_index_filename = config.get('INDEX', 'topics_labels_index_filename')
typeahead_index_filename = config.get('INDEX', 'typeahead_index_filename')

files_index = indexfiles.loader.FilesIndex(os.path.join(index_folder, files_index_filename))
#    files_dates_index = indexfiles.loader.FilesDatesIndex(os.path.join(index_folder, files_dates_index_filename))
topics_index = indexfiles.loader.TopicsIndex(os.path.join(index_folder, topics_index_filename))
typeahead_index = indexfiles.loader.TopicsTypeAheadIndex(os.path.join(index_folder, typeahead_index_filename)).index
typeahead_index_full = typeahead_index  # keep this version since the typeahead index is dynamically re-calculated
topics_occurrences_index = indexfiles.loader.TopicsOccurrencesIndex(os.path.join(index_folder,
                                                                                 topics_occurrences_index_filename))
topics_labels_index = indexfiles.loader.TopicsLabelsIndex(os.path.join(index_folder, topics_labels_index_filename))

# Initialize the main business components
processor = semantic.QueryProcessor(files_index=files_index,
                                    topics_occurrences_index=topics_occurrences_index,
                                    topics_labels_index=topics_labels_index,
                                    topics_index=topics_index)
finder = proximity.ProximityFinder(topics_index=topics_index,
                                   topics_occurrences_index=topics_occurrences_index,
                                   files_index=files_index)

# Set up UI
w = 850  # width for the Tk root
h = 720  # height for the Tk root
root = Tk()
root.title('Semantic Search')
root.minsize(width=w, height=h)
# get screen width and height
ws = root.winfo_screenwidth()  # width of the screen
hs = root.winfo_screenheight()  # height of the screen
# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
# set the dimensions of the screen
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

# Create application components
mainframe = ttk.Frame(root, padding="3 3 12 12")

search_entry = AutoCompleteEntry(mainframe, listboxLength=10, width=32)
search_button = Button(mainframe, text='Search', command=search_documents_by_topics)
reset_button = Button(mainframe, text='Reset', command=reset_gui)

topics_list = ttk.Treeview(mainframe, columns=('id', 'lbl_en', 'lbl_fr'), displaycolumns=0, height=12)
topics_list.column(0, width=20)
topics_list.bind('<Button-1>', topic_selected)

results_frame = ttk.Frame(mainframe)
results_list = ttk.Treeview(results_frame, height=12)
results_list.bind('<Button-1>', result_selected)
yscroll_result = ttk.Scrollbar(results_frame, orient=VERTICAL, command=results_list.yview)
results_list['yscrollcommand'] = yscroll_result.set

signature = StringVar()
semantic_signature_text = Text(mainframe, height=12, width=35)

proximity_frame = ttk.Frame(mainframe)
proximity_results = Text(proximity_frame, width=115, height=25)
yscroll_proximity = ttk.Scrollbar(proximity_frame, orient=VERTICAL, command=proximity_results.yview)
proximity_results['yscrollcommand'] = yscroll_proximity.set

# Position elements on screen
mainframe.grid(column=0, row=0, columnspan=6, rowspan=3, sticky=(N, W, E, S))
search_entry.grid(row=0, column=0, sticky=W)
search_button.grid(row=0, column=1, sticky=W)
reset_button.grid(row=0, column=2, sticky=W)
topics_list.grid(sticky=(W, E), row=1, column=0, columnspan=2)
results_frame.grid(row=1, column=2, sticky=(W, E), columnspan=2)
results_list.grid(row=0, column=0, sticky=(W, E))
yscroll_result.grid(row=0, column=1, sticky=(N, S))
semantic_signature_text.grid(row=1, column=4, sticky=(S, N, W))
proximity_frame.grid(row=2, column=0, columnspan=6, sticky=(W, E))
proximity_results.grid(row=0, column=0, columnspan=5, sticky=(W, E))
yscroll_proximity.grid(row=0, column=5, sticky=(N, S))

# Configure elements
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

# Give some extra space around elements
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Custom style
s = ttk.Style()
s.configure('TopicsList.Treeview', background='grey')

# Lift off!!!
root.mainloop()
