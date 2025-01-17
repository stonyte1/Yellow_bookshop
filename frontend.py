import PySimpleGUI as sg
from backend import Product, Customer, SecurityQuestions, Order, engine, session
from funkcijos import LentelesFunkcijos
import time

class BookshopGUI():

    def __init__(self):
        self.shoping_order = []

    def get_product_list(self, query=session.query(Product).all()):
        self.products = query
        product_list = []
        for item in self.products:           
            product_list.append([item.id, 
                                 item.book_name, 
                                 item.author, 
                                 item.realease_date, 
                                 item.price, item.quantity])
        return product_list

    def add_to_oder_cart(self, table, values):
        selected_rows = table.SelectedRows
        if selected_rows:
            selected_row = self.get_product_list()[values["-TABLE-"][0]]
            self.shoping_order.append(selected_row[1:])
            print(selected_row)
            return self.shoping_order

    def shopping_oder(self, customer_id):
        sg.theme("LightGreen5")
        headers =["Book name", "Author", "Release year", "Price"]
        layout =[
            [sg.Table(values=self.shoping_order, 
                        headings=headers,
                        auto_size_columns=True,
                        key="order_table",
                        enable_events=True)],
            [sg.Button("Remove", key="remove"), 
             sg.Button("Purchase", key="purchase"), 
             sg.Button("Close Shopping Order", key="close")]
        ]
        shopcart = sg.Window("Shoping Order", layout)
        while True:
            event, values = shopcart.read()
            if event in (sg.WIN_CLOSED, 'close'):
                break
            elif event == "remove":
                selected_rows = values["order_table"][0]
                print(selected_rows)
                del self.shoping_order[selected_rows]
                shopcart["order_table"].update(values=self.shoping_order)
            elif event == "purchase":
                for product in self.get_product_list():
                    for product_order in self.shoping_order:
                        if product[1] in product_order[0]:
                            LentelesFunkcijos(Product).set_element(product[0], quantity=Product.quantity - 1)
                        product_id = session.query(Product.id).filter(Product.book_name==product_order[0]).first()
                LentelesFunkcijos(Order).add_element(customer_id=customer_id[0], product_id=product_id[0])

                for product in self.get_product_list():
                    if product[5] <= 0:
                        LentelesFunkcijos(Product).delete_element(product[0])
                self.shoping_order.clear()
                shopcart["order_table"].update(values=self.shoping_order)
                self.loading_window()

        shopcart.close()

    def purchase_history(self, customer_id):
        orders_history = []
        query = session.query(Order.id, Product.book_name, Product.author, Order.date, Product.price).join(Order.products).join(Order.customer).filter(Customer.id==customer_id[0]).all()
        for order in query:
            order_list = list(order)
            orders_history.append(order_list)
        sg.theme("LightGreen5")
        headers = ["ID", "Book name", "Author", "Order date", "Price"]
        layout = [
            [sg.Table(values=orders_history, headings=headers, auto_size_columns=True, key="history_table")],
            [sg.Button("Close Purchase History", key="close")]
        ]
        history = sg.Window("Shoping History", layout)
        while True:
            event, values = history.read()
            if event in (sg.WIN_CLOSED, 'close'):
                break
        history.close()
    
    def loading_window(self):
        layout = [
            [sg.Text('Confirming order', size=(20, 1), justification='center')],
            [sg.ProgressBar(50, orientation='h', size=(20, 20), key='progressbar')]
        ]
        window = sg.Window('Loading order...', layout, finalize=True)

        for bar_range in range(100):
            event, values = window.read(timeout=50)
            if event == sg.WINDOW_CLOSED:
                break
            window['progressbar'].update_bar(bar_range + 10)
            time.sleep(0.00001)
    
        window.close()    
        sg.popup('You have successfully purchased books')
    
    def filter_by_author(self):
        filtered_books = session.query(Product).order_by(Product.author).all()
        return self.get_product_list(query=filtered_books)
    
    def filter_by_year(self):
        filtered_books_y = session.query(Product).order_by(Product.realease_date).all()
        return self.get_product_list(query=filtered_books_y)

class Login:
    def __init__(self):
        # lists
        self.lst_customer_emails = []
        self.lst_customer_s_keys = []
        self.lst_customer_pass = []
        for customer in LentelesFunkcijos(Customer).get_table_el_list():
            self.lst_customer_emails.append(customer.email)
            self.lst_customer_s_keys.append(customer.security_key)
            self.lst_customer_pass.append(customer.password)
        self.customer_id = 0

        # List in order for sg.Combo to work (in register_page)
        self.list_s_questions = []
        for s_question in LentelesFunkcijos(SecurityQuestions).get_table_el_list():
            self.list_s_questions.append(s_question.question_text)
        
    def forgot_page(self):
        layout = [
            [sg.Text('E-mail: '), sg.Input(key="-EMAIL-")],
            [sg.Text('Security key: '), sg.Input(key="-SECURITY-")],
            [sg.Button("Back", key="-ENTER-"),
            sg.Button("Exit", key="-EXIT-"),
            sg.Button("Remember my password", key="-REMEMBER-"),
            sg.Button("Register", key='-REGISTER-')]]
        
        forgot_window = sg.Window('Forgot password page', layout)

        while True:
            event, values = forgot_window.read()

            if event in (sg.WIN_CLOSED, '-EXIT-'):
                forgot_window.close()
                return self.customer_id
            elif event == '-REMEMBER-':
                email = values['-EMAIL-']

                if values['-EMAIL-'] not in self.lst_customer_emails:
                    sg.Popup('Wrong email')
                    continue
                if values['-SECURITY-'] not in self.lst_customer_s_keys:
                    sg.Popup('Wrong security key, Your security question is \n{}'.format(session.query(SecurityQuestions.question_text).filter(Customer.email==values['-EMAIL-']).join(Customer.question).one()[0]))
                    continue
                else:
                    sg.Popup("E-mail: {0}\nPassword: {1}".format(session.query(Customer.email).filter(Customer.email==values['-EMAIL-']).one()[0], session.query(Customer.password).filter(Customer.email==values['-EMAIL-']).one()[0]))
            elif event == '-REGISTER-':
                forgot_window.close()
                return self.register_page()
            elif event == '-ENTER-':
                forgot_window.close()
                return self.login_page()


    def login_page(self):
        self.__init__()
        layout =[
            [sg.Text('E-mail: '), sg.Input(key="-EMAIL-")],
            [sg.Text('Password: '), sg.Input(password_char='*', key="-PASS-")],
            [sg.Button("login", key="-ENTER-"),
            sg.Button("Exit", key="-EXIT-"),
            sg.Button("Forgot password", key="-FORGOT-"),
            sg.Button("Register", key='-REGISTER-')]
        ]
        login_window = sg.Window("Login", layout)
        while True:
            event, values = login_window.read()
            if event in (sg.WIN_CLOSED, '-EXIT-'):
                break
                
            elif event == '-ENTER-':
                if values['-EMAIL-'] not in self.lst_customer_emails:
                    sg.Popup('Wrong email')
                    continue
                if values['-PASS-'] not in self.lst_customer_pass:
                    sg.Popup('Wrong password')
                    continue
                else:
                    sg.Popup('Login sucessful')
                    login_window.close()
                    self.customer_id = session.query(Customer.id).filter(Customer.email==values['-EMAIL-']).one()
                    break
            elif event == '-FORGOT-':
                login_window.close()
                self.customer_id = self.forgot_page()
                break
            elif event == '-REGISTER-':
                login_window.close()
                self.customer_id = self.register_page()
                break
        return self.customer_id
    def register_page(self):
        layout =[
            [sg.Text('E-mail: '), sg.Input(key="-EMAIL-")],
            [sg.Text('Name: '), sg.Input(key="-NAME-")],
            [sg.Text('Surname: '), sg.Input(key="-SURNAME-")],
            [sg.Text('Password: '), sg.Input(password_char='*', key="-PASS-")],
            [sg.Text('Repeat Password: '), sg.Input(password_char='*', key="-REPEAT_PASS-")],
            [sg.Text('Security question'), sg.Combo(self.list_s_questions, default_value=self.list_s_questions[0], enable_events=True, readonly=True, key='-COMBO-')],
            [sg.Text('Security key: '), sg.Input(key="-SECURITY-")],
            [sg.Button('Exit', key="-EXIT-"),
            sg.Button('Register', key="-REGISTER-"),
            sg.Button('Back', key="-ENTER-")]]
        
        register_window = sg.Window('Register page', layout)

        while True:
            event, values = register_window.read()

            if event in (sg.WIN_CLOSED, '-EXIT-'):
                register_window.close()
                return self.customer_id

            elif event == '-REGISTER-':
                if "@" not in values["-EMAIL-"]:
                    sg.Popup('Please enter valid Email')
                    continue
                if values["-PASS-"] != values["-REPEAT_PASS-"]:
                    sg.Popup('Passwords doesnt match')
                    continue
                if values['-NAME-'] == '' or values['-SURNAME-'] == '':
                    sg.Popup('Please enter full name')
                    continue
                else:
                    s_question = session.query(SecurityQuestions.id).filter(SecurityQuestions.question_text==values['-COMBO-']).one()[0]
                    LentelesFunkcijos(Customer).add_element(name=values['-NAME-'], 
                                                            surname=values['-SURNAME-'], 
                                                            email=values["-EMAIL-"],
                                                            password=values["-PASS-"],
                                                            security_key=values["-SECURITY-"],
                                                            question_id=s_question)
                    register_window.close()
                    return self.login_page()
            elif event == "-ENTER-":
                register_window.close()
                return self.login_page()




