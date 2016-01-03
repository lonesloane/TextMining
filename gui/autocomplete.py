import logging
from Tkinter import *
import ttk

from analysis import typeahead
from index import loader
import search.semantic_query as semantic
from index.loader import TopicsIndex


class AutoCompleteEntry(ttk.Entry):
    def __init__(self, *args, **kwargs):
        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

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
        self.listframe = ttk.Frame()
        empty_frame = ttk.Frame(self.listframe)
        empty_frame.grid()

    def changed(self, name, index, mode):
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
                self.listframe.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                if not self.listboxUp:
                    self.topics_typeahead_list = ttk.Treeview(self.listframe,
                                                              height=self.listboxLength,
                                                              columns=('id', 'lbl_en', 'lbl_fr'),
                                                              displaycolumns=0)
                    self.topics_typeahead_list.column(0, width=60)
                    self.topics_typeahead_list.bind("<Button-1>", self.selection)
                    self.topics_typeahead_list.bind("<Right>", self.selection)
                    self.topics_typeahead_list.grid(row=0, column=0)
                    self.scroll = ttk.Scrollbar(self.listframe, orient=VERTICAL,
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
        self.logger.debug('looking up matching labels for: %s', self.var.get())
        self.logger.debug('nb matches found: %s', len(typeahead_index[self.var.get()]))
        return typeahead_index[self.var.get()]

    def selection(self, event):
        if self.listboxUp:
            selected_index = self.topics_typeahead_list.selection()
            selected_item = self.topics_typeahead_list.item(selected_index)
            values = selected_item['values']
            self.logger.debug('Selection: %s', values[0])
            self.var.set('')

            topics_list.insert('', END, text=values[1], values=(values[0], values[1], values[2]))

            self.topics_typeahead_list.destroy()
            self.scroll.destroy()
            self.logger.debug('redraw topics list...3')
            self.listboxUp = False
            self.icursor(END)

    def move_up(self, event):
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

    def move_down(self, event):
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
    topics_ids = [str(topics_list.item(topic_id)['values'][0]) for topic_id in topics_list.get_children()]
    logging.getLogger(__name__).info('Searching documents for topics: %s', topics_ids)

    matching_documents, matching_topics = processor.execute(topics_ids)
    logging.getLogger(__name__).debug('Found documents for topics: %s', matching_documents)
    logging.getLogger(__name__).debug('Found topics: %s', matching_topics)

    for result in results_list.get_children():
        results_list.delete(result)
    for document in matching_documents:
        results_list.insert('', END, text=document)

    global typeahead_index
    typeahead_index = typeahead.IndexBuilder().build(topics_index=build_topics_index(matching_topics))


def build_topics_index(matching_topics):
    result = dict()
    logging.getLogger(__name__).debug('Begin build_topics_index')
    for uri in matching_topics:
        if uri not in result:
            result[uri] = topics_index[str(uri)]

    logging.getLogger(__name__).debug('result: %s', result)

    return result


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

    files_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Files_Index'
    topics_occurrences_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Occurrences_Index'
    topics_labels_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Labels_Index'

#    topics_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index'
#    topics_index = TopicsIndex(topics_index_filename).index
    topics_index = TopicsIndex().index

#    processor = semantic.QueryProcessor(files_index_filename=files_index_filename,
#                                        topics_occurrences_index_filename=topics_occurrences_index_filename,
#                                        topics_labels_index_filename=topics_labels_index_filename)
    processor = semantic.QueryProcessor()

    typeahead_index_filename = '../output/Topics_Typeahead_Index'
#    typeahead_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Typeahead_Index'
    typeahead_index = loader.TopicsTypeAheadIndex(typeahead_index_filename).index

    w = 800  # width for the Tk root
    h = 650  # height for the Tk root
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

    topics_frame = ttk.Frame(mainframe)
    topics_list = ttk.Treeview(topics_frame, columns=('id', 'lbl_en', 'lbl_fr'), displaycolumns=0, height=10)
    topics_list.column(0, width=120)
    results_frame = ttk.Frame(mainframe)
    results_list = ttk.Treeview(results_frame, height=10)

    # Position elements on screen
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    search_entry.grid(row=0, column=0)
    search_button.grid(row=0, column=1)
    topics_frame.grid(row=1, column=0, columnspan=2)
    topics_list.grid()
    results_frame.grid(row=1, column=2)
    results_list.grid()

    # Configure elements
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    # Give some extra space around elements
    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.mainloop()
