import logging
from Tkinter import *
import ttk

from index import loader
import search.semantic_query as semantic


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

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.listboxUp:
                self.listframe.destroy()
                self.listboxUp = False
        else:
            words = self.get_matching_labels()
            if words:
                self.logger.debug('self.listboxUp ? %s', self.listboxUp)
                self.listframe = ttk.Frame()
                self.listframe.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                if not self.listboxUp:
                    self.listbox = Listbox(self.listframe, width=self["width"], height=self.listboxLength)
                    self.listbox.bind("<Button-1>", self.selection)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.grid(row=0, column=0)
                    self.scroll = ttk.Scrollbar(self.listframe, orient=VERTICAL, command=self.listbox.yview)
                    self.listbox['yscrollcommand'] = self.scroll.set
                    self.scroll.grid(row=0, column=1, sticky=(N, S))
                    self.listboxUp = True

                self.listbox.delete(0, END)
                for w in words:
                    self.listbox.insert(END, w)

            else:
                if self.listboxUp:
                    self.listframe.destroy()
                    self.listboxUp = False

    def get_matching_labels(self):
        self.logger.debug('looking up matching labels for: %s', self.var.get())
        self.logger.debug('nb matches found: %s', len(typeahead_index[self.var.get()]))
        return typeahead_index[self.var.get()]

    def selection(self, event):
        if self.listboxUp:
            self.var.set(self.listbox.get(ACTIVE))
            topics_list.insert('', END, text=self.get())
            self.listbox.destroy()
            self.scroll.destroy()
            self.logger.debug('redraw topics list...3')
            self.listboxUp = False
            self.icursor(END)

    def move_up(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]

            if index != '0':
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)

                self.listbox.see(index)  # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def move_down(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]

            if index != END:
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)

                self.listbox.see(index)  # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)


def search_documents_by_topics():
    topics = [topics_list.item(child)["text"] for child in topics_list.get_children()]
    logging.getLogger(__name__).info('Searching documents for topics: %s', topics)

    matching_documents, matching_topics = processor.execute(topics)
    results_list.delete(0, END)
    for document in matching_documents:
        results_list.insert(END, document)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

    files_index_filename='/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Files_Index'
    topics_occurrences_index_filename='/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Occurrences_Index'
    topics_labels_index_filename='/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Labels_Index'
    processor = semantic.QueryProcessor(files_index_filename=files_index_filename,
                                        topics_occurrences_index_filename=topics_occurrences_index_filename,
                                        topics_labels_index_filename=topics_labels_index_filename)
#    typeahead_index_filename = '../output/Topics_Typeahead_Index'
    typeahead_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Typeahead_Index'
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
#    topics_list = Listbox(topics_frame)
    topics_list = ttk.Treeview(topics_frame)
    results_frame = ttk.Frame(mainframe)
    results_list = Listbox(results_frame, height=10 )

    # Position elements on screen
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    search_entry.grid(row=0, column=0)
    search_button.grid(row=0, column=1)
    topics_frame.grid(row=1, column=2)
    topics_list.grid()
    results_frame.grid(row=1, column=3)
    results_list.grid()

    # Configure elements
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    # Give some extra space around elements
    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.mainloop()
