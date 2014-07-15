# -*- coding: iso-8859-15 -*-
#Titel: Teaterekonomi
#Författare: Jonathan Böcker
#Datum: 2014-05-18
#
#Det här är ett program för hantering av ett antal teatrars biljettförsäljning
#Programmets information om teatrarna lagras i en fil med namnet "teatrar.txt"
#mellan körningarna.
#Filens syntax är:
#namn/antal platser/pris vuxenbiljett/pris barnbiljett/pris pensionärbiljett

import os
from tkinter import *
from tkinter import ttk
from random import choice

#En klass som beskriver en teater:
#	name - namnet på teatern
#	seats - totalt antal platser i salongen
#	price_adult - pris på vuxenbiljett
#	price_child - pris på barnbiljett
#	price_senior - pris på pensionärsbiljett
#	sold_adult - sålda vuxenbiljetter
#	sold_child - sålda barnbiljetter
#	sold_senior - sålda pensionärsbiljetter
#	percentage_sold - beläggning i procent
#	sum_income - summan av intäkterna
class Theater:
	def __init__(self, name, seats, price_adult, price_child, price_senior):
		self.name = name
		self.seats = seats
		self.price_adult = price_adult
		self.price_child = price_child
		self.price_senior = price_senior
		self.sold_adult = IntVar()
		self.sold_child = IntVar()
		self.sold_senior = IntVar()
		self.percentage_sold = IntVar()
		self.sum_income = IntVar()

	def __str__(self):
		return self.name

#En klass som ritar ett nytt fönster med lösningarna
#från calculate_tickets()
#	solution_list - lista från calculate_tickets som ska presenteras
#	box_message - meddelande från calculate_tickets som ska presenteras om solution_list är tom
class draw_new_window():
	def __init__(self, solution_list, box_message):
		self.top = Toplevel()
		self.top.resizable(True, True)
		self.top.grid_columnconfigure(0, weight=1)
		self.top.grid_rowconfigure(0, weight=1)

		if len(solution_list) != 0:
			self.top.title("Möjliga lösningar")
			self.scrollbar = ttk.Scrollbar(self.top, orient="vertical")
			self.canvas = Canvas(self.top, yscrollcommand=self.scrollbar.set,
								width=250, height=100)
			self.scrollbar.grid(column=1, row=0, sticky=(N,S))
			self.scrollbar.configure(command=self.canvas.yview)
			self.canvas.grid(column=0, row=0, sticky=NSEW)
			self.canvas.columnconfigure(0, weight=1)
			self.canvas.rowconfigure(0, weight=1)

			self.frame = ttk.Frame(self.canvas)
			self.frame.grid(column=0, row=0, sticky=NSEW)
			self.frame.rowconfigure(0, weight=1)

			self.canvas.create_window((0,0),window=self.frame,anchor='nw', tags="frame")

			self.frame.bind("<Configure>", self.OnFrameConfigure)

			self.text = ["Alternativ: ", "Vuxna ", "Pensionärer ", "Barn"]
			for x, y in enumerate(self.text):
				ttk.Label(self.frame, text=y).grid(column=x, row=1, sticky=NSEW)

			for x, y in enumerate(solution_list):
				t =str(x+1) + ":"
				ttk.Label(self.frame, text=t, anchor=E).grid(column=0, row=x+2, sticky=NSEW)
				for t, k in enumerate(y):
					ttk.Label(self.frame, text=k, anchor="center").grid(column=t+1, row=x+2, sticky=NSEW)
			self.sg = ttk.Sizegrip(self.top)
			self.sg.grid(column=1, row=1, sticky=(S,E))
		else:
			self.top.title("Information")
			self.tiny_frame = ttk.Frame(self.top, padding="12 12 12 12")
			self.tiny_frame.grid(column=0, row=0)
			self.title_label = ttk.Label(self.tiny_frame, text=box_message)
			self.title_label.grid(column=0, row=0, sticky=NSEW)
			self.button = Button(self.tiny_frame, text="Okay", command=self.top.destroy)
			self.button.grid(column=0, row=1)

	#Metod som kallas så fort fönstrets storlek ändras.
	#Uppdaterar området som skall scrollas.
	def OnFrameConfigure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))

#Öppnar och läser in filen med informationen om teatrarna
#och skapar ett objekt för varje teater och lägger dem i en lista.
#IN = Filens namn(string)
#OUT = En lista med "Theater" objekt
def create_list(FILENAME):
	f = open(FILENAME, "r")
	theaters = []
	parts = []
	for line in f:
		parts = line.strip().split('/')

		#I fall "parts" inte är 5 lång, görs "theaters" tom och loopen bryts.
		if len(parts) != 5:
			theaters = []
			break
		else:
			theaters.append(Theater(parts[0], int(parts[1]),
			int(parts[2]), int(parts[3]), int(parts[4])))
	f.close()
	return theaters

#Räknar ut samtliga teatrars beläggning, intäkter,
#Samt summan av alla teatrars intäkter.
#Kallar på draw_new_window och presenterar en sorterad lista. 
def present_profits(event=None):
	for thing in theater_list:
		try:
			thing.percentage_sold.set(int(((thing.sold_adult.get()
			+ thing.sold_child.get() + thing.sold_senior.get()) / thing.seats) * 100))
		except ValueError:
			continue
		try:
			thing.sum_income.set(((thing.sold_adult.get() * thing.price_adult)
			+ (thing.sold_child.get() * thing.price_child) + (thing.sold_senior.get() * thing.price_senior)))
		except ValueError:
			continue
	sum_all_theaters_income.set(0) 

	#Sorterar även listan med teatrar med hänseende på utförsäljning
	sorted_theater_list = sorted(theater_list, key=lambda Theater: Theater.percentage_sold.get(), reverse=True)

	empty_message = ""
	calculated_message = "Sorterad lista efter procent utsålt: \n \n"

	for thing in sorted_theater_list:
		sum_all_theaters_income.set(thing.sum_income.get() + sum_all_theaters_income.get())

		calculated_message += str(thing.name + "  " + str(thing.sum_income.get()) + "kr  " +
			str(thing.percentage_sold.get()) + "%" + "\n")
	
	#Skapar nytt fönster med sorterade listan presenterad
	profits_window = draw_new_window(empty_message, calculated_message)

#Räknar ut antal biljetter av varje sort när användaren väljer teater
#och skriver in kassans storlek
def calculate_tickets(event=None):
	solution_list = []
	box_message = ""
	choice = choose_theater.current()
	try:
		amount = amount_to_calculate.get()
	except ValueError:
		amount = 0
	max_amount = theater_list[choice].price_adult * theater_list[choice].seats
	if amount <= max_amount and amount > 0:
		for antvuxna in range(0, theater_list[choice].seats+1):
			for antpens in range(0, theater_list[choice].seats+1):
				if (amount - (theater_list[choice].price_adult * antvuxna + theater_list[choice].price_senior * antpens)) % theater_list[choice].price_child == 0:
					antbarn = (amount - (theater_list[choice].price_adult * antvuxna + theater_list[choice].price_senior * antpens)) / theater_list[choice].price_child
					if antbarn >= 0:
						solution_list.append((int(antvuxna),int(antpens),int(antbarn)))
		if len(solution_list) == 0:
			box_message = "Det fanns inga möjliga lösningar"

	elif amount <= 0:
		box_message = "Kan bara räkna på kassor större än 0 kr"
	else:
		box_message= "Förtjänsten kan max bli " + str(max_amount) + "kr på en kväll för denna teatern"

	#Kallar på draw_new_window
	solution_window = draw_new_window(solution_list, box_message)

#Skapar ett nytt fönster och visar information om vald teater
def show_info():
	top2 = Toplevel()
	top2.title("Teaterinfo")
	infoframe = ttk.Frame(top2, padding="3 3 12 12")
	infoframe.grid(column=0, row=0, sticky=NSEW)
	infoframe.columnconfigure(0, weight=1)
	infoframe.rowconfigure(0, weight=1)

	theater_to_show = choose_theater.current()
	text_to_show = (theater_list[theater_to_show].name + "\n" + str(theater_list[theater_to_show].seats) + " platser\n\n" +
		str(theater_list[theater_to_show].price_adult) + "kr för en vuxenbiljett\n" + str(theater_list[theater_to_show].price_senior) +
		"kr för en pensionärsbiljett\n" +str(theater_list[theater_to_show].price_child) + "kr för en barnbiljett\n")

	max_profits = "Max förtjänst på en kväll:\n" + str(theater_list[theater_to_show].seats * theater_list[theater_to_show].price_adult) + "kr"

	ttk.Label(infoframe, text=text_to_show).grid(column=1, row=1, sticky=(W,E))
	ttk.Label(infoframe, text=max_profits).grid(column=1, row=2, sticky=(W,E))
	button = Button(infoframe, text="Okay", command=top2.destroy)
	button.grid(column=1, row=3)

#Skapar ett fönster och visar ett felmeddelande error_message
def error_window():
	ttk.Label(mainframe, text=error_message, justify="center").grid(column=1, row=1, sticky=(W, E))


# Huvudprogram
#Den grafiska delen initieras här.
root = Tk()
root.title("Teater ekonomi")
root.resizable(True, True)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=NSEW)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

secondframe = ttk.Frame(root, padding="3 3 12 12")
secondframe.grid(column=0, row=1, sticky=NSEW)
secondframe.columnconfigure(0, weight=1)
secondframe.rowconfigure(0, weight=1)


FILENAME = "teatrar.txt"
error_message = ""

#Felkontroll av filen "teatrar.txt"
#Kontrollerar om create_list() kan köras utan fel. Ger felmeddelande annars.
try:
	theater_list = create_list(FILENAME)
except ValueError:
	error_message = "Filen 'teatrar.txt' är korrupt.\nProgrammet kan inte fortsätta."

#Kontrollerar att filen finns, och om den inte gör det så ges felmeddelande.
except FileNotFoundError:
	error_message = "Filen 'teatrar.txt' existerar inte eller är inte i programmappen.\nProgrammet kan inte fortsätta."

if len(error_message) != 0:
	error_window()

elif len(theater_list) == 0:
	error_message = "Filen 'teatrar.txt' är tom eller korrupt.\nProgrammet kan inte fortsätta"
	error_window()

#
#
else:
	headlines = []
	theater_names_col = []
	theater_ticket_one = []
	theater_ticket_two = []
	theater_ticket_three = []
	theater_perc_row = []
	theater_profits_row = []

	headlines.append(ttk.Label(mainframe, text="Teatrar"))
	headlines.append(ttk.Label(mainframe, text="Vuxenbiljetter"))
	headlines.append(ttk.Label(mainframe, text="Barnbiljetter"))
	headlines.append(ttk.Label(mainframe, text="Pensionärbiljetter"))
	headlines.append(ttk.Label(mainframe, text="Procent fullsatt"))
	headlines.append(ttk.Label(mainframe, text="Inkomst för kvällen"))

	headlines[0].grid(column=1, row=0, sticky=NSEW)
	headlines[1].grid(column=2, row=0, sticky=NSEW)
	headlines[2].grid(column=4, row=0, sticky=NSEW)
	headlines[3].grid(column=6, row=0, sticky=NSEW)
	headlines[4].grid(column=8, row=0, sticky=NSEW)
	headlines[5].grid(column=10, row=0, sticky=NSEW)

	for y in headlines:
		y.columnconfigure(0, weight=1)
		y.rowconfigure(0, weight=1)

	for x, y in enumerate(theater_list):
		st1 = ttk.Label(mainframe, text="st")
		st1.grid(column=3, row=x+2, sticky=NSEW)
		st1.columnconfigure(0, weight=1)

		st2 = ttk.Label(mainframe, text="st")
		st2.grid(column=5, row=x+2, sticky=NSEW)
		st2.columnconfigure(0, weight=1)

		st3 = ttk.Label(mainframe, text="st")
		st3.grid(column=7, row=x+2, sticky=NSEW)
		st3.columnconfigure(0, weight=1)

		percent = ttk.Label(mainframe, text="%")
		percent.grid(column=9, row=x+2, sticky=NSEW)
		percent.columnconfigure(0, weight=1)

		kr = ttk.Label(mainframe, text="kr")
		kr.grid(column=11, row=x+2, sticky=NSEW)
		kr.columnconfigure(0, weight=1)

		info = y.name + " (" + str(y.seats) + "st)"

		theater_names_col.append(ttk.Label(mainframe, text=info))
		theater_ticket_one.append(ttk.Entry(mainframe, textvariable=y.sold_adult, justify="right", width=10))
		theater_ticket_two.append(ttk.Entry(mainframe, textvariable=y.sold_child, justify="right", width=10))
		theater_ticket_three.append(ttk.Entry(mainframe, textvariable=y.sold_senior, justify="right", width=10))
		theater_perc_row.append(ttk.Label(mainframe, textvariable=y.percentage_sold, anchor=E))
		theater_profits_row.append(ttk.Label(mainframe, textvariable=y.sum_income, anchor=E))

		theater_names_col[x].grid(column=1, row=x+2, sticky=NSEW)
		theater_ticket_one[x].grid(column=2, row=x+2, sticky=NSEW)
		theater_ticket_two[x].grid(column=4, row=x+2, sticky=NSEW)
		theater_ticket_three[x].grid(column=6, row=x+2, sticky=NSEW)
		theater_perc_row[x].grid(column=8, row=x+2, sticky=NSEW)
		theater_profits_row[x].grid(column=10, row=x+2, sticky=NSEW)

		theater_names_col[x].columnconfigure(0, weight=1)
		theater_ticket_one[x].columnconfigure(0, weight=1)
		theater_ticket_two[x].columnconfigure(0, weight=1)
		theater_ticket_three[x].columnconfigure(0, weight=1)
		theater_perc_row[x].columnconfigure(0, weight=1)
		theater_profits_row[x].columnconfigure(0, weight=1)

		theater_names_col[x].rowconfigure(0, weight=1)
		theater_ticket_one[x].rowconfigure(0, weight=1)
		theater_ticket_two[x].rowconfigure(0, weight=1)
		theater_ticket_three[x].rowconfigure(0, weight=1)
		theater_perc_row[x].rowconfigure(0, weight=1)
		theater_profits_row[x].rowconfigure(0, weight=1) 

		theater_ticket_one[x].bind('<Return>', present_profits)
		theater_ticket_two[x].bind('<Return>', present_profits)
		theater_ticket_three[x].bind('<Return>', present_profits)

	ttk.Label(mainframe, text="Summa alla teatrar").grid(column=10, row=len(theater_list)+2, sticky=NSEW)

	sum_all_theaters_income = IntVar()

	ttk.Label(mainframe, textvariable=sum_all_theaters_income, anchor=E).grid(column=10, row=len(theater_list)+3, sticky=NSEW)
	ttk.Label(mainframe, text="kr").grid(column=11, row=len(theater_list)+3, sticky=NSEW)

	enterbutton1 = ttk.Button(mainframe, text="Kalkylera", command=present_profits)
	enterbutton1.grid(column=8, row=len(theater_list)+2, sticky=E, rowspan=2, columnspan=2)

	#Här kommer andra ramen
	choose_theater_list = []
	amount_to_calculate = IntVar()

	#Lista med alla teaternamn
	for x in theater_list:
		choose_theater_list.append(x.name)
	
	infolabel = ttk.Label(secondframe, text="Räkna utifrån en kassa hur många biljetter som sålts")
	infolabel.grid(column=1, row=0, columnspan=3)

	infolabel2 = ttk.Label(secondframe, text="Kassa:")
	infolabel2.grid(column=4, row=0)

	enterbutton2 = ttk.Button(secondframe, text="Visa info", command=show_info)
	enterbutton2.grid(column=1, row=1, sticky=W)

	enterbutton3 = ttk.Button(secondframe, text="     Kalkylera\nKan ta lång tid!", command=calculate_tickets)
	enterbutton3.grid(column=2, row=1, sticky=W)

	choose_theater = ttk.Combobox(secondframe, values=choose_theater_list)
	choose_theater.grid(column=3, row=1, sticky=W)
	choose_theater.state(["readonly"])
	choose_theater.set(choose_theater_list[0])

	amount_money_box = ttk.Entry(secondframe, textvariable=amount_to_calculate, justify="right", width=7)
	amount_money_box.grid(column=4, row=1, sticky=W)
	amount_money_box.bind('<Return>', calculate_tickets)

	ttk.Label(secondframe, text="kr").grid(column=5, row=1, sticky=W)

	#Ett intro-meddelande som förklarar snabbt vad programmet gör i ett nytt fönster.
	empty_list = []
	tutorial_message = """Det här programmet räknar ut teatrars försäljning och förtjänst på en kväll.\n
Teatrarnas information lagras i en fil 'teatrar.txt'. Syntaxen för filen hittas i källkoden.\n
Skriv in antal biljetter som sålts och tryck Enter i ett av fälten eller tryck 'Kalkylera'\n
"""
	tutorial_window = draw_new_window(empty_list, tutorial_message)

for child in mainframe.winfo_children(): child.grid_configure(padx=2, pady=2)
for child in secondframe.winfo_children(): child.grid_configure(padx=2, pady=2)

root.mainloop()





