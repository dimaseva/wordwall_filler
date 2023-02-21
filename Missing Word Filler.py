import customtkinter as CTk
from main import prepare_driver, first_enter, enter_by_cookies, get_sentences, create_game
import random

font = ('Helvetica', 15,  'bold')
width = 625

meme = [
'войти через куки',
'войти через коки',
'ева лучшая',
'тук-тук налоговая'
]


class CustomBtn(CTk.CTkButton):
    def __init__(self, sentense, **kwargs):
        super().__init__(**kwargs)
        self.sentence = sentense

class App(CTk.CTk):
    def __init__(self, driver, **kwargs):
        super().__init__(**kwargs)

        self.driver = driver

        self.geometry(f'{width}x500')
        self.title("Wordwall Filler")
        self.resizable(False, False)

        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2

        self.geometry("+%d+%d" % (x, y))

        self.main_frame = CTk.CTkFrame(master=self, width=400, height=350,  fg_color="royal blue")
        self.second_frame = CTk.CTkFrame(master=self, width=600,  fg_color="royal blue")
        self.phrase_frame = CTk.CTkFrame(master=self, width=900, height=500)
        self.end_frame = CTk.CTkFrame(master=self, width=400, height=350,  fg_color="royal blue")
        


        self.setup_main_frame()
        self.setup_second_frame()
        self.setup_phrase_frame()
        self.setup_end_frame()
        
        # self.show_phrase1()
        # self.show_phrase2()
        # self.show_phrase3()
        self.show_main()
        # self.show_end()
        # self.e1.grid(row=3, column=0)





    #btn func --------------------------------------------------------------

    def login(self):
        self.info_label.configure(text_color='royal blue')
        user = self.log_entry.get()
        password = self.pass_entry.get()
        if first_enter(self.driver, user, password):
            self.show_second()
        else:
            self.info_label.configure(text_color='white')
        
    def login_cookie(self):
        self.info_label.configure(text_color='royal blue')
        if enter_by_cookies(self.driver):
            self.show_second()
        else:
            self.cookie_btn.configure(state="disabled")
            self.info_label.configure(text_color='white')

    def take_name_n_count(self, *args):
        self.second_info_label.configure(text_color='royal blue')
        self.sentences_count = self.count_entry.get()
        self.game_name = self.name_entry.get()
        try:
            if not self.game_name or not self.sentences_count.isnumeric():
                self.second_info_label.configure(text_color='white')
            else:
                self.sentences_count = int(self.sentences_count)
                self.show_phrase1()
        except:
            self.second_info_label.configure(text_color='white')

    def take_sentences(self, *args):
        self.phrase = self.phrase_find_entry.get()
        if self.phrase:
            result = get_sentences(self.driver, self.phrase)
            #change 1 to self.cur_page
            if result:
                self.total = result['total']
                self.sentences = result['sentences']
                self.info_label_phrase.configure(text="")
                for i, sentence in enumerate(self.sentences):
                    label = CTk.CTkTextbox(master=self.frame_buttons, width=510, height=90, font=font, border_color='grey', border_width=3, fg_color='transparent', text_color='snow')
                    label.insert('insert', sentence)
                    start = sentence.lower().find(self.phrase)
                    label.tag_add('word', f'1.{start}', f'1.{start + len(self.phrase)}')
                    label.tag_config('word', foreground="pale green")
                    label.configure(state= "disabled")
                    label.grid(row=i, column=0)
                    
                    btn = CTk.CTkButton(master=self.frame_buttons, width=90, height=90, bg_color='transparent', fg_color='grey23', border_color='light blue', border_width=2, text='Choose', font=font, command = lambda s=sentence : self.sentence_choose(s))
                    btn.grid(column=1, row=i)

                self.frame_buttons.update_idletasks()
                self.canvas.config(scrollregion=self.canvas.bbox("all"))

                self.show_phrase2()
                
            else:
                self.info_label_phrase.configure(text="Sorry haven't collected")
        else:
            self.info_label_phrase.configure(text="Complete the phrase line")

    def sentence_choose(self, sentence):
        self.selected = sentence

        self.textbox_sentence_edit.insert('insert', self.selected)

        start = self.selected.lower().find(self.phrase)
        self.textbox_sentence_edit.tag_add('word', f'1.{start}', f'1.{start + len(self.phrase)}')
        self.textbox_sentence_edit.tag_config('word', foreground="pale green")

        self.missed_words_entry.insert('insert', self.phrase + ',')

        self.show_phrase3()

    def add_to_list(self, *args):
        miss_list = []
        incorect_list = []

        if self.textbox_sentence_edit.get("1.0", 'end') != '\n':

            for word in self.missed_words_entry.get().strip().split(','):
                if not word:
                    continue
                start = self.selected.find(word)
                if start != -1:
                    miss_list.append((start, len(word)))

                else:
                    self.info_label_phrase.configure(text="Can't find a phrase/word. Please recheck")
                    return

            incorect_list = [word for word in self.wrong_words_entry.get().strip().split(',')]

            if len(miss_list) < 2:
                self.info_label_phrase.configure(text="There must be at least 2 items")
                return

            self.list_of_settings.append({
                        'sentence' : self.selected,
                        'miss' : miss_list,
                        'incorect' : incorect_list
                    })
            self.curr += 1
            self.check_curr_sentence()

        else:
            self.info_label_phrase.configure(text="Don't leave the suggestion box empty")

    def check_curr_sentence(self):
        if self.curr < self.sentences_count:
            self.counter_label.configure(text=f'#{self.curr+1}')
            self.clean_up()
            self.show_phrase1()

        else:
            self.make_game()

    def make_game(self):

        create_game(self.driver, self.game_name, self.sentences_count, self.list_of_settings)
        # print(self.game_name, int(self.sentences_count), self.list_of_settings)
        self.end_info.configure(text='Done!')
        self.e1.grid(row=3, column=0)

        self.show_end()

    def another_game(self):
        self.name_entry.delete(0, 'end')
        self.count_entry.delete(0, 'end')

        self.clean_up()

        self.show_second()

    def clean_up(self):
        self.phrase_find_entry.delete(0, 'end')
        self.canvas.delete("all")
        self.frame_buttons.grid_forget()
        self.frame_buttons = CTk.CTkFrame(master=self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_buttons, anchor='nw')
        self.textbox_sentence_edit.delete(1.0, 'end')
        self.missed_words_entry.delete(0, 'end')
        self.wrong_words_entry.delete(0, 'end')
        self.vsb._command('moveto', 0)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")








    #showing screens ------------------------------------------------------

    def show_main(self):
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')

    def show_second(self):
        self.main_frame.place_forget()
        self.end_frame.place_forget()
        self.second_frame.place(relx=0.5, rely=0.5, anchor='center')
        self.list_of_settings = []
        self.curr = 0
        self.e1.grid_forget()
        self.bind('<Return>', self.take_name_n_count)

    def show_phrase1(self):
        self.second_frame.place_forget()
        self.p3.grid_forget()
        # self.phrase_frame.place(relx=0.1, rely=0.1, anchor='s')
        self.phrase_frame.grid(row=0, column=0)
        self.p1.grid(row=2, column=0)
        self.bind('<Return>', self.take_sentences)

    def show_phrase2(self):
        self.p1.grid_forget()
        self.p2.grid(row=2, column=0)
        self.bind('<Return>', lambda x : 1)

    def show_phrase3(self):
        self.p2.grid_forget()
        self.p3.grid(row=2, column=0)
        self.bind('<Return>', self.add_to_list)

    def show_end(self):
        self.phrase_frame.grid_forget()
        self.end_frame.place(relx=0.5, rely=0.5, anchor='center')
        self.bind('<Return>', lambda x : 1)





    #setuping screens ---------------------------------------------------------

    def setup_main_frame(self):
        self.f1 = CTk.CTkFrame(master=self.main_frame, width=400, height=350, fg_color='transparent')
        self.f1.grid(row=0, column=0)
        
        self.log_label = CTk.CTkLabel(master=self.f1, text='Login:', width=100, font=font)
        self.log_label.grid(row=0, column=0)

        self.log_entry = CTk.CTkEntry(master=self.f1, width=200, font=font)
        self.log_entry.grid(row=0, column=1)

        self.pass_label = CTk.CTkLabel(master=self.f1, text='Password:', width=100, font=font)
        self.pass_label.grid(row=1, column=0)

        self.pass_entry = CTk.CTkEntry(master=self.f1, width=200, font=font)
        self.pass_entry.grid(row=1, column=1)

        self.info_label = CTk.CTkLabel(master=self.main_frame, text='Failed to enter', width=100, font=font, text_color='royal blue')
        self.info_label.grid(row=1, column=0)

        self.f2 = CTk.CTkFrame(master=self.main_frame, width=400, height=350,  fg_color="royal blue")
        self.f2.grid(row=2, column=0)


        self.enter_btn = CTk.CTkButton(master=self.f2, text='Enter', width=100, fg_color='black', font=font, command=self.login)
        self.enter_btn.grid(column=0, row=0)

        self.none_label = CTk.CTkLabel(master=self.f2, text_color='royal blue')
        self.none_label.grid(column=0, row=1)


        self.cookie_btn = CTk.CTkButton(master=self.f2, text='Enter By Cookies', width=100, fg_color='black', font=font, command=self.login_cookie)
        self.cookie_btn.grid(column=0, row=2)

        if random.randint(0,100) < 25:
            self.cookie_btn.configure(text=random.choice(meme))

    def setup_second_frame(self):
        #bind there
        

        self.a1 = CTk.CTkFrame(master=self.second_frame, width=600, height=500, fg_color='transparent')
        self.a1.grid(row=0, column=0)

        self.name_label = CTk.CTkLabel(master=self.a1, text='Enter game name:', width=100, font=font)
        self.name_label.grid(row=0, column=0)

        self.name_entry = CTk.CTkEntry(master=self.a1, width=200, font=font)
        self.name_entry.grid(row=0, column=1)

        self.count_label = CTk.CTkLabel(master=self.a1, text='Number of sentences:', width=150, font=font)
        self.count_label.grid(row=1, column=0, padx=10)

        self.count_entry = CTk.CTkEntry(master=self.a1, width=200, font=font)
        self.count_entry.grid(row=1, column=1)

        self.second_info_label = CTk.CTkLabel(master=self.second_frame, font=font, text='Fill in the fields correctly', text_color='royal blue')
        self.second_info_label.grid(column=0, row=1)

        self.next_btn = CTk.CTkButton(master=self.second_frame, text='Next', width=100, fg_color='black', font=font, command=self.take_name_n_count)
        self.next_btn.grid(column=0, row=2, pady=2)
        
#set\choose\edit frame
#make unbind
    def setup_phrase_frame(self):
        #bind there

        self.counter_label = CTk.CTkLabel(master=self.phrase_frame, width=width,  font=('Helvetica', 40,  'bold'), text='#1', fg_color='royal blue')
        self.counter_label.grid(column=0, row=0)

        self.info_label_phrase = CTk.CTkLabel(master=self.phrase_frame, text='', font=font)
        self.info_label_phrase.grid(row=1, column=0)

        self.phrase_frame1()
        self.phrase_frame2()
        self.phrase_frame3()

    def phrase_frame1(self):

        self.p1 = CTk.CTkFrame(master=self.phrase_frame, width=600, height=350, fg_color='transparent')


        self.added_frame = CTk.CTkFrame(master=self.p1, width=600, height=350, fg_color='transparent')
        self.added_frame.grid(row=0, column=0)

        self.phrase_find_label = CTk.CTkLabel(master=self.added_frame, text='Enter a phrase or word:', width=100, font=font)
        self.phrase_find_label.grid(row=0, column=0, padx=10)

        self.phrase_find_entry = CTk.CTkEntry(master=self.added_frame, width=200, font=font)
        self.phrase_find_entry.grid(row=0, column=1)



        self.next_btn_frame = CTk.CTkButton(master=self.p1, text='Find', width=100, fg_color='black', font=font, command=self.take_sentences)
        self.next_btn_frame.grid(column=0, row=1, pady=5)


    def phrase_frame2(self):

        self.p2 = CTk.CTkFrame(master=self.phrase_frame, width=600, height=500)
#___________________________________________________________ here height of canvas
        self.canvas = CTk.CTkCanvas(master=self.p2, width=600,height=450, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.grid(row=0, column=0, sticky="news")

        self.vsb = CTk.CTkScrollbar(master=self.p2, orientation="vertical", command=self.canvas.yview, width=20)
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        self.frame_buttons = CTk.CTkFrame(master=self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_buttons, anchor='nw')

    def phrase_frame3(self):

        self.p3 = CTk.CTkFrame(master=self.phrase_frame, width=600, height=350, fg_color='transparent')

        self.textbox_sentence_edit = CTk.CTkTextbox(master=self.p3, width=510, height=90, font=font, border_color='grey', border_width=3, fg_color='transparent', text_color='snow')
        self.textbox_sentence_edit.grid(row=0, column=0)

        self.pass_label1 = CTk.CTkLabel(master=self.phrase_frame, text='', font=font)
        self.pass_label1.grid(row=1, column=0)


        self.words_frame = CTk.CTkFrame(master=self.p3, width=600, height=350, fg_color='transparent')
        self.words_frame.grid(row=2, column=0)

        self.missed_words_label = CTk.CTkLabel(master=self.words_frame, text='Missed words (Filling example: "word,phrase,word")', width=100, font=font)
        self.missed_words_label.grid(row=0, column=0)

        # self.sv = CTk.StringVar()
        # self.sv.trace("w", self.change_color_textbox)

        self.missed_words_entry = CTk.CTkEntry(master=self.words_frame, width=400, font=font)#, textvariable=self.sv)
        self.missed_words_entry.grid(row=1, column=0)

        self.wrong_words_label = CTk.CTkLabel(master=self.words_frame, text='Incorrect words (Filling example: "word,phrase,word")', width=100, font=font)
        self.wrong_words_label.grid(row=3, column=0)

        self.wrong_words_entry = CTk.CTkEntry(master=self.words_frame, width=400, font=font)
        self.wrong_words_entry.grid(row=4, column=0)

        self.pass_label2 = CTk.CTkLabel(master=self.words_frame, text='', font=font)
        self.pass_label2.grid(row=5, column=0)

        self.btn_sentence_done = CTk.CTkButton(master=self.words_frame, text='Done', width=100, fg_color='royal blue', font=font, command=self.add_to_list)
        self.btn_sentence_done.grid(column=0, row=6)

    #TODO: if need change dynamic color use this
    # def change_color_textbox(self, *args):
    #     words = self.sv.get().split(',')
    #     sentence = self.textbox_sentence_edit.get("1.0", 'end')
    #     sentence_list = sentence.split(' ')
    #     print(words, sentence_list, sep='\n')
    #     for word in words:
    #         for part in sentence_list:
    #             if part == word:
    #                 start = sentence.lower().find(word)
    #                 self.textbox_sentence_edit.tag_add(word, f'1.{start}', f'1.{start + len(word)+1}')
    #                 self.textbox_sentence_edit.tag_config(word, foreground="pale green")

    # def exit(self):
    #     self.driver.close()
    #     import sys
    #     sys.exit()

    def setup_end_frame(self):
        self.pass_label3 = CTk.CTkLabel(master=self.end_frame, text='', font=font)
        self.pass_label3.grid(row=0, column=0)

        self.end_info = CTk.CTkLabel(master=self.end_frame, text='Wait Please', width=304, font=font, text_color='white')
        self.end_info.grid(row=1, column=0)
        

        self.pass_label4 = CTk.CTkLabel(master=self.end_frame, text='', font=font)
        self.pass_label4.grid(row=2, column=0)

        self.e1 = CTk.CTkFrame(master=self.end_frame, width=400, height=500, fg_color='transparent')

        
        self.another_one = CTk.CTkButton(master=self.e1, text='Another one', width=100, fg_color='black', font=font, command=self.another_game)
        self.another_one.grid(column=0, row=0, )

        self.pass_label5 = CTk.CTkLabel(master=self.e1, text='', width=100,  font=font)
        self.pass_label5.grid(column=1, row=0,)

        self.exit = CTk.CTkButton(master=self.e1, text='Quit', width=100, fg_color='black', font=font, command=self.destroy)
        self.exit.grid(column=2, row=0,)



if __name__ == "__main__":
    dr = prepare_driver()
    app = App(dr)
    app.mainloop()
    dr.quit()
    