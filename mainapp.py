from frontend import *
import PySimpleGUI as sg
import time

headers = ['ID', 'Book Title', "Author", 'Year of Release', 'Price', 'Quantity']
table = sg.Table(values=BookshopGUI().get_product_list(), headings=headers, 
    auto_size_columns=True, key="-TABLE-", enable_events=True)

layout = [
    [table],
    [sg.Button("ADD TO CART"), 
        sg.Button("VIEW CART"), 
        sg.Button("FILTER BOOKS BY AUTHOR"), 
        sg.Button("FILTER BOOKS BY THE YEAR"), 
        sg.Button("EXIT"), 
        sg.Button("VIEW PURCHASE HISTORY"),
        sg.Button("CONFIRM ORDER")]
    ]    

window = sg.Window("BOOK_SHOP", layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'EXIT':
        break
    elif event == 'ADD TO CART':
        pass
    elif event == 'VIEW CART':
        BookshopGUI().shopping_oder()
    elif event == 'FILTER BOOKS BY AUTHOR':
        pass
    elif event == 'FILTER BOOKS BY YEAR':
        pass
    elif event == 'VIEW PURCHASE HISTORY':
        BookshopGUI.purchase_history()
    elif event == 'CONFIRM ORDER':
        BookshopGUI().loading_window()
window.close()

