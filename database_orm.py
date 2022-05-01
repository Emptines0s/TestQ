import models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd


class Database:
    engine = create_engine('sqlite:///LabData.db')
    Session = sessionmaker(engine)

    # создать все таблицы
    def create_tables(self):
        models.Base.metadata.create_all(self.engine)

    # удалить все таблицы
    def delete_tables(self):
        models.Base.metadata.drop_all(self.engine)

    # экспортировать данные таблиц БД в файлы json
    def export_data(self, table_list, file_path='export', file_name='export_file'):
        try:
            for table in table_list:
                dataframe = pd.read_sql(sql=table, con=self.engine)
                dataframe.to_json(fr'{file_path}\{table}_{file_name}.json')
        except Exception as e:
            print(e)

    # импортировать данные из json файлов в соответствующие таблицы в БД
    def import_data(self, file_list, table_list):
        try:
            table_list.sort()
            for file in file_list:
                dataframe = pd.read_json(file)
                file_name = file.split('/')[-1]
                for table in reversed(table_list):
                    if table + '_' in file_name:
                        table_list.remove(table)
                        dataframe.to_sql(name=table, con=self.engine, if_exists='append', index=False)
                        break
        except Exception as e:
            print(e)

    # добавить сформированный объект (строчку/строчки) в выбранную таблицу
    def add_item(self, data, table_name):
        try:
            dataframe = pd.DataFrame(data=[data])
            dataframe.to_sql(name=table_name, con=self.engine, if_exists='append', index=False)
        except Exception as e:
            print(e)

    # удалить выбранный объект/объекты
    def delete_item(self, table_name, attribute, value):
        try:
            with self.Session.begin() as session:
                target_item = session.query(table_name).filter(attribute == value).all()
                for item in target_item:
                    session.delete(item)
        except Exception as e:
            print(e)

    # обновить выбранный объект
    def update_item(self, table_name, attribute, value, update_values):
        try:
            with self.Session.begin() as session:
                session.query(table_name).filter(attribute == value).update(update_values)
        except Exception as e:
            print(e)

    # добавить дочерние элементы выбранному объекту по связям: один ко многим и многие ко многим
    def append_items(self, p_table_name, p_attribute, p_value, p_relationship, c_table_name, c_attribute, c_values):
        try:
            with self.Session.begin() as session:
                parent_item = session.query(p_table_name).filter(p_attribute == p_value).first()
                for c_value in c_values:
                    child_item = session.query(c_table_name).filter(c_attribute == c_value).first()
                    getattr(parent_item, p_relationship).append(child_item)
        except Exception as e:
            print(e)

    # удалить дочерние элементы выбранного объекта
    def remove_child(self, table_name, attribute, value, p_relationship):
        try:
            with self.Session.begin() as session:
                parent_item = session.query(table_name).filter(attribute == value).first()
                getattr(parent_item, p_relationship).clear()
        except Exception as e:
            print(e)

    # получить информацию только об одном конкретном объекте (строчки) в выбранной таблице
    def fetch_item_data(self, *table_args, attribute, value):
        try:
            with self.Session.begin() as session:
                target = session.query(*table_args).filter(attribute == value).all()
        except Exception as e:
            print(e)
        return target

    # получить дочерние элементы объекта (пример: тесты -> вопросы теста)
    def fetch_child_items(self, table_name, attribute, value, p_relationship):
        try:
            with self.Session.begin() as session:
                parent_item = session.query(table_name).filter(attribute == value).first()
                child_item_list = getattr(parent_item, p_relationship)
                data = [item.__dict__ for item in child_item_list]
                dataframe = pd.DataFrame(data)
        except Exception as e:
            print(e)
        return dataframe


database = Database()
