import sys

import database_orm as db

from PyQt5.QtWidgets import QApplication, QListWidgetItem, QWidget, QDialog, QListWidget, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5 import QtGui
from PyQt5.QtCore import Qt


# Окно формы входа
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
        user_data = database.fetch_item_data(db.User.user_id,
                                             db.User.user_password,
                                             db.User.user_level,
                                             attribute=db.User.user_login,
                                             value=login)
        print(user_data)
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
        database.add_item(data=data, table_name='user')


# Виджет на основе QListWidget с методами drag and drop для импорта пользовательских пакетов в формате json
class FileList(QListWidget):
    def __init__(self):
        super(FileList, self).__init__()

        self.setAcceptDrops(True)
        self.setStyleSheet(
            "background-color: rgb(180, 182, 169);"
            "border: 2px solid white;"
            "border-radius: 8px;"
            "color: rgb(44, 44, 44);"
            "background-image: url(image/dropfile.png);"
            "background-position: center;"
            "background-repeat: no-repeat;"
            "background-attachment: fixed;"
        )
        self.itemDoubleClicked.connect(self._delete_item)

    def _delete_item(self, item):
        self.takeItem(self.row(item))

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        if e.mimeData().hasUrls():
            e.setDropAction(Qt.CopyAction)
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        if e.mimeData().hasUrls():
            e.setDropAction(Qt.CopyAction)
            e.accept()
            links = [url.toLocalFile() for url in e.mimeData().urls() if url.toLocalFile().endswith('.json')]
            self.addItems(links)
        else:
            e.ignore()


# Главное окно
class MainWindow(QWidget):
    def __init__(self, user_id, user_level):
        super(MainWindow, self).__init__()

        loadUi('main_window.ui', self)

        self.user_id = user_id
        self.user_level = user_level
        self.current_editable_test = None
        self.current_question = None
        self.go_to_profile_page()

        self.pushButton_profile.clicked.connect(self.go_to_profile_page)
        self.pushButton_test_list.clicked.connect(self.go_to_test_list_page)
        self.pushButton_edit.clicked.connect(self.go_to_creation_page)
        self.pushButton_start_test.clicked.connect(self.go_to_test)
        self.pushButton_add_answer.clicked.connect(self.add_answer)
        self.pushButton_change.clicked.connect(self.save_question_changes)
        self.pushButton_create_question.clicked.connect(self.create_question)
        self.pushButton_delete.clicked.connect(self.delete_question)
        self.pushButton_save_test.clicked.connect(self.create_save_test_window)
        self.pushButton_sign_out.clicked.connect(self.go_to_login_window)
        self.pushButton_import_export.clicked.connect(self.go_to_import_export_page)
        self.pushButton_export.clicked.connect(self.export_data)
        self.pushButton_import.clicked.connect(self.import_data)

        self.listWidget_tests.itemClicked.connect(self.choice_of_test)
        self.listWidget_all_questions.itemClicked.connect(self.choice_of_question)
        self.listWidget_test_questions.itemClicked.connect(self.choice_of_question)

        self.file_list = FileList()
        self.horizontalLayout_6.insertWidget(1, self.file_list, 2)

        self.show()

    def go_to_profile_page(self):
        self.stackedWidget.setCurrentWidget(self.profile_page)
        user_data = database.fetch_item_data(db.User.user_login,
                                             attribute=db.User.user_id,
                                             value=self.user_id)
        self.label_10.setText(user_data[0]['user_login'])
        user_result = database.fetch_child_items(table_name=db.User,
                                                 attribute=db.User.user_id,
                                                 value=self.user_id,
                                                 p_relationship='tests')
        self.tableWidget.setRowCount(len(user_result.index))
        for i, row in user_result.iterrows():
            test_data = database.fetch_item_data(db.Test.test_name,
                                                 attribute=db.Test.test_id,
                                                 value=row['test_id'])
            self.tableWidget.setItem(i, 0, QTableWidgetItem(test_data[0]['test_name']))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(row['result']))
            percentage_result = str(float(row['result'].split('/')[0])/float(row['result'].split('/')[1])*100)
            self.tableWidget.setItem(i, 2, QTableWidgetItem(percentage_result + '%'))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str(row['datetime'])))

    def go_to_test_list_page(self):
        self.stackedWidget.setCurrentWidget(self.test_list_page)
        test_list = database.fetch_item_data(db.Test.test_id, db.Test.test_name,
                                             attribute=None,
                                             value=None)
        self.listWidget_tests.clear()
        for test in test_list:
            current_test = QListWidgetItem(test['test_name'], self.listWidget_tests). \
                setWhatsThis(str(test['test_id']))
            self.listWidget_tests.addItem(current_test)
        self.listWidget_tests.setCurrentRow(0)
        self.choice_of_test(item=self.listWidget_tests.currentItem())

    def go_to_test(self):
        self.test_widget = TestWindow(test=self.listWidget_tests.currentItem().whatsThis(), user_id=self.user_id)
        self.verticalLayout_21.addWidget(self.test_widget)
        self.stackedWidget_core.setCurrentWidget(self.test_page)
        self.test_widget.pushButton_back_to_tests.clicked.connect(self.go_to_main)

    def go_to_main(self):
        self.stackedWidget_core.setCurrentWidget(self.main_page)

    def go_to_import_export_page(self):
        self.stackedWidget.setCurrentWidget(self.import_export_page)

    def export_data(self):
        file_path = self.lineEdit_export_file_path.text()
        file_name = self.lineEdit_export_file_name.text()
        if len(file_path) == 0:
            file_path = 'export'
        if len(file_name) == 0:
            file_name = 'export_file'
        if self.comboBox.currentIndex() == 2:
            table_list = ['test', 'test_question', 'question', 'answer']
        elif self.comboBox.currentIndex() == 1:
            table_list = ['question', 'answer']
        elif self.comboBox.currentIndex() == 0:
            table_list = ['test']
        database.export_data(table_list=table_list,
                             file_path=file_path,
                             file_name=file_name)

    def import_data(self):
        file_list = [self.file_list.item(number).text()
                     for number in range(self.file_list.count())]
        database.import_data(file_list=file_list,
                             table_list=['test', 'test_question', 'question', 'answer'])

    def go_to_creation_page(self):
        self.stackedWidget.setCurrentWidget(self.creation_page)
        self.choise_dialog = ChoiceWindow()
        self.choise_dialog.pushButton_change.clicked.connect(self.loading_test_question)
        self.choise_dialog.pushButton_new_test.clicked.connect(self.loading_all_question)

    def loading_all_question(self):
        questions = database.fetch_item_data(db.Question.question_name, db.Question.question_id,
                                             attribute=None,
                                             value=None)
        self.listWidget_all_questions.clear()
        self.listWidget_test_questions.clear()
        for question in questions:
            current_question = QListWidgetItem(question['question_name'], self.listWidget_all_questions). \
                setWhatsThis(str(question['question_id']))
            self.listWidget_all_questions.addItem(current_question)

    def loading_test_question(self):
        self.current_editable_test = self.choise_dialog.change_test()
        if self.current_editable_test is not None:
            self.loading_all_question()
            questions = database.fetch_child_items(table_name=db.Test,
                                                   attribute=db.Test.test_id,
                                                   value=self.current_editable_test,
                                                   p_relationship='questions')
            print(questions)
            for i, row in questions.iterrows():
                current_question = QListWidgetItem(row['question_name'], self.listWidget_test_questions). \
                    setWhatsThis(str(row['question_id']))
                self.listWidget_test_questions.addItem(current_question)

    def create_save_test_window(self):
        self.save_dialog = SaveWindow(test=self.current_editable_test)
        self.save_dialog.pushButton_save_changes.clicked.connect(self.save_test)

    def save_test(self):
        data = self.save_dialog.test_data()
        data.update({'test_question_count': self.listWidget_test_questions.count()})
        if self.current_editable_test is None:
            database.add_item(data=data, table_name='test')
            test_list = database.fetch_item_data(db.Test.test_id, db.Test.test_name,
                                                 attribute=None,
                                                 value=None)
            question_list = [self.listWidget_test_questions.item(number).whatsThis()
                             for number in range(self.listWidget_test_questions.count())]
            database.append_items(p_table_name=db.Test,
                                  p_attribute=db.Test.test_id,
                                  p_value=test_list[-1]['test_id'],
                                  p_relationship='questions',
                                  c_table_name=db.Question,
                                  c_attribute=db.Question.question_id,
                                  c_values=question_list)
        else:
            database.update_item(table_name=db.Test,
                                 attribute=db.Test.test_id,
                                 value=self.current_editable_test,
                                 update_values=data)
            database.remove_child(table_name=db.User,
                                  attribute=db.User.user_id,
                                  value=self.current_editable_test,
                                  p_relationship='tests')
            question_list = [self.listWidget_test_questions.item(number).whatsThis()
                             for number in range(self.listWidget_test_questions.count())]
            database.append_items(p_table_name=db.Test,
                                  p_attribute=db.Test.test_id,
                                  p_value=self.current_editable_test,
                                  p_relationship='questions',
                                  c_table_name=db.Question,
                                  c_attribute=db.Question.question_id,
                                  c_values=question_list)
        self.loading_all_question()

    def create_question(self):
        self.current_question = None
        self.lineEdit_question_name.clear()
        self.textEdit_question_description.clear()

        if self.verticalLayout_13 is not None:
            for i in reversed(range(self.verticalLayout_13.count())):
                self.verticalLayout_13.itemAt(i).widget().deleteLater()

    def delete_question(self):
        database.delete_item(table_name=db.Question,
                             attribute=db.Question.question_id,
                             value=self.current_question)
        self.lineEdit_question_name.clear()
        self.textEdit_question_description.clear()
        for i in reversed(range(self.verticalLayout_13.count())):
            self.verticalLayout_13.itemAt(i).widget().deleteLater()
        for i in reversed(range(self.listWidget_test_questions.count())):
            if self.listWidget_test_questions.item(i).whatsThis() == self.current_question:
                self.listWidget_test_questions.takeItem(i)
        for i in reversed(range(self.listWidget_all_questions.count())):
            if self.listWidget_all_questions.item(i).whatsThis() == self.current_question:
                self.listWidget_all_questions.takeItem(i)
        self.current_question = None
        self.choice_of_question(item=self.current_question)

    def add_answer(self):
        answer_block = AnswerBlock(answers=None)
        self.verticalLayout_13.addWidget(answer_block)

    def save_question_changes(self):
        name = self.lineEdit_question_name.text()
        description = self.textEdit_question_description.toPlainText()
        if self.current_question is None:
            data = {'question_name': name,
                    'question_description': description}
            database.add_item(data=data, table_name='question')
            question_list = database.fetch_item_data(db.Question.question_id, db.Question.question_name,
                                                     attribute=None,
                                                     value=None)
            for answer in range(self.verticalLayout_13.count()):
                answer_data = {
                    'answer_content': self.verticalLayout_13.itemAt(answer).widget().textEdit_answer.toPlainText(),
                    'is_correct': self.verticalLayout_13.itemAt(answer).widget().radioButton_is_correct.isChecked(),
                    'question_id': question_list[-1]['question_id']}
                database.add_item(data=answer_data, table_name='answer')
            current_question = QListWidgetItem(question_list[-1]['question_name'], self.listWidget_all_questions). \
                setWhatsThis(str(question_list[-1]['question_id']))
            self.listWidget_all_questions.addItem(current_question)
        else:
            data = {'question_name': name,
                    'question_description': description}
            database.update_item(table_name=db.Question,
                                 attribute=db.Question.question_id,
                                 value=self.current_question,
                                 update_values=data)
            database.delete_item(table_name=db.Answer,
                                 attribute=db.Answer.question_id,
                                 value=self.current_question)
            for answer in range(self.verticalLayout_13.count()):
                answer_data = {
                    'answer_content': self.verticalLayout_13.itemAt(answer).widget().textEdit_answer.toPlainText(),
                    'is_correct': self.verticalLayout_13.itemAt(answer).widget().radioButton_is_correct.isChecked(),
                    'question_id': self.current_question}
                database.add_item(data=answer_data, table_name='answer')
            for i in reversed(range(self.listWidget_test_questions.count())):
                if self.listWidget_test_questions.item(i).whatsThis() == self.current_question:
                    self.listWidget_test_questions.item(i).setText(name)
            for i in reversed(range(self.listWidget_all_questions.count())):
                if self.listWidget_all_questions.item(i).whatsThis() == self.current_question:
                    self.listWidget_all_questions.item(i).setText(name)

    def choice_of_question(self, item):
        if item is not None:
            self.current_question = item.whatsThis()
            question_data = database.fetch_item_data(db.Question.question_name, db.Question.question_description,
                                                     attribute=db.Question.question_id,
                                                     value=self.current_question)
            self.lineEdit_question_name.setText(question_data[0]['question_name'])
            self.textEdit_question_description.setText(question_data[0]['question_description'])
            answers = database.fetch_child_items(table_name=db.Question,
                                                 attribute=db.Question.question_id,
                                                 value=self.current_question,
                                                 p_relationship='answers')

            for i in reversed(range(self.verticalLayout_13.count())):
                self.verticalLayout_13.itemAt(i).widget().deleteLater()

            for i, row in answers.iterrows():
                answer_block = AnswerBlock(answers=row)
                self.verticalLayout_13.addWidget(answer_block, i)
        else:
            self.lineEdit_question_name.clear()
            self.textEdit_question_description.clear()
            for i in reversed(range(self.verticalLayout_13.count())):
                self.verticalLayout_13.itemAt(i).widget().deleteLater()

    def choice_of_test(self, item):
        if item is not None:
            test_data = database.fetch_item_data(db.Test.test_name,
                                                 db.Test.test_description,
                                                 db.Test.test_question_count,
                                                 attribute=db.Test.test_id,
                                                 value=item.whatsThis())
            self.label_test_name.setText(test_data[0]['test_name'])
            self.textBrowser_test_description.setText(test_data[0]['test_description'])
            self.label_test_question_count.setText(f"Количество вопросов: {str(test_data[0]['test_question_count'])}")
        else:
            self.label_test_name.setText('Название теста')
            self.textBrowser_test_description.setText('Описание теста')
            self.label_test_question_count.setText("Количество вопросов: X")

    def go_to_login_window(self):
        self.close()
        self.login_window = LoginWindow()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        try:
            self.choise_dialog.close()
            self.save_dialog.close()
        except Exception as e:
            print(e)


# Виджет блока ответа
class AnswerBlock(QWidget):
    def __init__(self, answers):
        super(AnswerBlock, self).__init__()

        loadUi('answer.ui', self)

        if answers is not None:
            self.textEdit_answer.setText(answers['answer_content'])
            self.radioButton_is_correct.setChecked(answers['is_correct'])
            self.setWhatsThis(str(answers['answer_id']))

        self.pushButton_delete_answer.clicked.connect(self._delete)

    def set_user_choice(self, item):
        self.pushButton_delete_answer.hide()
        if item is not None:
            self.radioButton_is_correct.setChecked(item)
        else:
            self.radioButton_is_correct.setChecked(False)

    def _delete(self):
        self.deleteLater()


# Окно выбора теста для редактирования
class ChoiceWindow(QDialog):
    def __init__(self):
        super(ChoiceWindow, self).__init__()

        loadUi('create_or_edit_window.ui', self)

        self.go_to_choice_page()

        self.pushButton_change_test.clicked.connect(self.go_to_test_list_page)
        self.pushButton_back.clicked.connect(self.go_to_choice_page)
        self.pushButton_change.clicked.connect(self._delete)
        self.pushButton_new_test.clicked.connect(self._delete)
        self.pushButton_delete_test.clicked.connect(self.delete_test)

        self.listWidget_tests.itemClicked.connect(self.choice_of_test)

        self.show()

    def go_to_test_list_page(self):
        self.stackedWidget.setCurrentWidget(self.test_list_page)
        test_list = database.fetch_item_data(db.Test.test_id, db.Test.test_name,
                                             attribute=None,
                                             value=None)
        self.listWidget_tests.clear()
        for test in test_list:
            current_test = QListWidgetItem(test['test_name'], self.listWidget_tests). \
                setWhatsThis(str(test['test_id']))
            self.listWidget_tests.addItem(current_test)
        self.listWidget_tests.setCurrentRow(0)
        self.choice_of_test(item=self.listWidget_tests.currentItem())

    def go_to_choice_page(self):
        self.stackedWidget.setCurrentWidget(self.choice_page)

    def choice_of_test(self, item):
        if self.listWidget_tests.currentItem() is not None:
            data = database.fetch_item_data(db.Test.test_name, db.Test.test_description,
                                            attribute=db.Test.test_id,
                                            value=item.whatsThis())
            self.label_test_name.setText(data[0]['test_name'])
            self.textBrowser_test_description.setText(data[0]['test_description'])
        else:
            self.label_test_name.setText('Название теста')
            self.textBrowser_test_description.setText('Описание теста')

    def delete_test(self):
        database.delete_item(table_name=db.Test,
                             attribute=db.Test.test_id,
                             value=self.listWidget_tests.currentItem().whatsThis())
        self.go_to_test_list_page()

    def change_test(self):
        if self.listWidget_tests.currentItem() is not None:
            return self.listWidget_tests.currentItem().whatsThis()
        else:
            return None

    def _delete(self):
        self.close()


# Окно сохранения редактируемого теста
class SaveWindow(QDialog):
    def __init__(self, test):
        super(SaveWindow, self).__init__()

        loadUi('save_test_window.ui', self)

        self.test = test

        self.pushButton_save_changes.clicked.connect(self._delete)
        self.pushButton_back.clicked.connect(self._delete)

        if self.test is not None:
            data = database.fetch_item_data(db.Test.test_name, db.Test.test_description,
                                            attribute=db.Test.test_id,
                                            value=test)
            self.lineEdit_test_name.setText(data[0]['test_name'])
            self.textEdit_test_description.setText(data[0]['test_description'])

        self.show()

    def test_data(self):
        name = self.lineEdit_test_name.text()
        description = self.textEdit_test_description.toPlainText()
        question_count = None
        data = {'test_name': name,
                'test_description': description,
                'test_question_count': question_count}
        return data

    def _delete(self):
        self.close()


# Окно прохождения теста
class TestWindow(QWidget):
    def __init__(self, test, user_id):
        super(TestWindow, self).__init__()

        loadUi('test_page.ui', self)

        self.test = test
        self.user_id = user_id
        self.question_list = None
        self.current_question = 0
        self.answer_list = []
        self.user_answers = []
        self.load_data()
        self.go_to_question(self.current_question)

        self.pushButton_previous.clicked.connect(self.go_to_previous)
        self.pushButton_next.clicked.connect(self.go_to_next)
        self.pushButton_back.clicked.connect(lambda: self.back_to_question(len(self.question_list.index)-1))
        self.pushButton_finish.clicked.connect(self.finish_test)
        self.pushButton_back_to_tests.clicked.connect(self._delete)

        self.listWidget_question.itemDoubleClicked.connect(self.back_to_question)

    def load_data(self):
        self.question_list = database.fetch_child_items(table_name=db.Test,
                                                        attribute=db.Test.test_id,
                                                        value=self.test,
                                                        p_relationship='questions')
        for i, row in self.question_list.iterrows():
            question_answers = database.fetch_child_items(table_name=db.Question,
                                                          attribute=db.Question.question_id,
                                                          value=row['question_id'],
                                                          p_relationship='answers')
            answer_dictionary = dict()
            for a_i, a_row in question_answers.iterrows():
                answer_dictionary.update({a_row['answer_id']: a_row['is_correct']})
            self.answer_list.append(answer_dictionary)
            self.user_answers.append(dict())
        print(self.answer_list)

    def go_to_previous(self):
        if self.current_question > 0:
            self.save_answer(item=self.current_question)
            self.current_question -= 1
            self.go_to_question(item=self.current_question)

    def go_to_next(self):
        if self.current_question < len(self.question_list.index) - 1:
            self.save_answer(item=self.current_question)
            self.current_question += 1
            self.go_to_question(item=self.current_question)
        else:
            self.save_answer(item=self.current_question)
            self.load_result()

    def go_to_question(self, item):
        self.label_question_description.setText(self.question_list.loc[item, 'question_description'])
        self.label_question_number.setText(f"{self.current_question + 1}/{len(self.question_list.index)}")
        question_answers = database.fetch_child_items(table_name=db.Question,
                                                      attribute=db.Question.question_id,
                                                      value=int(self.question_list.loc[item, 'question_id']),
                                                      p_relationship='answers')
        if self.verticalLayout_5 is not None:
            for i in reversed(range(self.verticalLayout_5.count())):
                self.verticalLayout_5.itemAt(i).widget().deleteLater()
        for i, row in question_answers.iterrows():
            answer_block = AnswerBlock(answers=row)
            answer_block.set_user_choice(item=self.user_answers[item].get(row['answer_id']))
            self.verticalLayout_5.addWidget(answer_block, i)

    def save_answer(self, item):
        for answer in range(self.verticalLayout_5.count()):
            answer_id = self.verticalLayout_5.itemAt(answer).widget().whatsThis()
            answer_is_correct = self.verticalLayout_5.itemAt(answer).widget().radioButton_is_correct.isChecked()
            self.user_answers[item].update({int(answer_id): answer_is_correct})
        print(self.user_answers)

    def back_to_question(self, item):
        if type(item) is not int:
            item = int(item.whatsThis())
        self.stackedWidget.setCurrentWidget(self.question_page)
        self.current_question = item
        self.go_to_question(item=item)

    def load_result(self):
        answers_count = 0
        self.stackedWidget.setCurrentWidget(self.result_page)
        self.listWidget_question.clear()
        for i, row in self.question_list.iterrows():
            current_question = QListWidgetItem(row['question_name'], self.listWidget_question). \
                setWhatsThis(str(i))
            self.listWidget_question.addItem(current_question)
            if True in self.user_answers[i].values():
                answers_count += 1
            else:
                self.listWidget_question.item(i).setForeground(QtGui.QColor('red'))
        self.label_completed_questions.setText(
            f"Вы ответили на {answers_count}/{len(self.question_list.index)} вопросов")

    def finish_test(self):
        user_score = 0
        self.stackedWidget.setCurrentWidget(self.finish_page)
        self.listWidget_correct_answer.clear()
        for i, row in self.question_list.iterrows():
            current_question = QListWidgetItem(row['question_name'], self.listWidget_correct_answer). \
                setWhatsThis(str(i))
            self.listWidget_question.addItem(current_question)
            if self.user_answers[i] == self.answer_list[i]:
                user_score += 1
                self.listWidget_correct_answer.item(i).setForeground(QtGui.QColor('green'))
            else:
                self.listWidget_correct_answer.item(i).setForeground(QtGui.QColor('red'))
        self.label_correct_answer.setText(
            f"Вы ответили правильно на {user_score}/{len(self.question_list.index)} вопросов. "
            f"Это {round(user_score/len(self.question_list.index), 1)*100}% правильных ответов!")
        data = {'user_id': self.user_id,
                'test_id': self.test,
                'result': f"{user_score}/{len(self.question_list.index)}"}
        database.add_item(data=data, table_name='user_test')

    def _delete(self):
        self.deleteLater()


if __name__ == "__main__":
    database = db.Database()
    database.create_tables()
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    app.exec()
