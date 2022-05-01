from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from database_orm import database


class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()

        loadUi('login_window.ui', self)

        self.pushButton_2.clicked.connect(self.go_to_main_window)
        self.pushButton.clicked.connect(self.create_account)

        self.show()

    def go_to_main_window(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        user_data = db.database.fetch_item_data(db.models.User.user_id,
                                                db.models.User.user_password,
                                                db.models.User.user_level,
                                                attribute=db.models.User.user_login,
                                                value=login)
        if len(user_data) == 1:
            if user_data[0]['user_password'] == password:
                self.close()
                self.main_window = MainWindow(user_id=user_data[0]['user_id'],
                                              user_level=user_data[0]['user_level'])

    def create_account(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        data = {'user_login': login,
                'user_password': password,
                'user_level': 'common'}
        db.database.add_item(data=data, table_name='user')