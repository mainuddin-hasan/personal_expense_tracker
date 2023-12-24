import os
import streamlit as st
import pandas as pd

from src.db_ops import show_data, edit_data, delete_data, select_columns, extra_field



def save_expense(cursor, db):    
    st.header('💸 Expense Entry')
    if 'flag' not in st.session_state:
        st.session_state.flag = 0

    df = pd.read_sql('''SELECT * FROM expense''', con=db)
    column_names,column_types = extra_field(df,db)
    col = select_columns(db)
    
    
    with st.form(key='expense_submit_form', clear_on_submit=True, border=True):
        
        expense_category = ['Shopping', 'Snacks', 'Mobile Recharge', 
                            'Online Course', 'Subscription', 'Others']
        
        values = []
        extra_val = []
        expense_date = st.date_input('Expense Date*')
        values.append(expense_date)
        
        category = st.selectbox('Expense Category*', expense_category)
        values.append(category)
        
        amount = st.text_input('Amount*')
        values.append(amount)
        
        notes = st.text_area('Notes')
        values.append(notes)
        
        for column_name, column_type in zip(column_names, column_types):
            # st.write(column_type.decode())
            if "varchar(512)" in column_type.decode(): 
                value = st.text_input(column_name)
                extra_val.append(value)
            elif column_type.decode() == "double":
                value = st.number_input(column_name)
                extra_val.append(value)
            elif column_type.decode() in ("longtext", "TEXT"): 
                value = st.text_area(column_name)
                extra_val.append(value)
            elif "date" in column_type.decode(): 
                value = st.date_input(column_name)
                extra_val.append(value)
            elif "timestamp" in column_type.decode(): 
                value = st.date_input(column_name)
                extra_val.append(value)
            else:
                st.write(f"Unsupported type for {column_name}: {column_type.decode()}")
                
        document_upload = st.file_uploader('Upload Document', 
                                           type=['txt','pdf', 
                                                 'jpg', 'png', 'jpeg'], 
                                            accept_multiple_files=True)
        # st.write(values)
        if st.form_submit_button(label='Submit'):
            if not(expense_date and category and amount):
                st.error('Please fill all the * fields')
            else:
                st.session_state.flag = 1


    if st.session_state.flag:


        with st.form(key='final', clear_on_submit=True, border=True):
  

            if st.form_submit_button('Are you Sure?'):
                st.session_state.flag = 0
                all_documents = []
                for file in document_upload:
                    if file is not None:
                        # Get the file name and extract the extension
                        file_name = file.name
                        # st.write(file_name)
                        file_extension = os.path.splitext(file_name)[1]
                        dir_name = "./documents/expenses"
                        if not os.path.isdir(dir_name):
                            os.makedirs(dir_name)

                        file_url = dir_name + '/' + file_name
                        # file_url = dir_name + file_name
                        all_documents.append(file_url)
                        doc = ", ".join(all_documents)
                        values.append(str(doc))
                        for val in range(len(extra_val)):
                            values.append(extra_val[val])
                        # st.write(str(values))
                        # val = str(all_documents)
                        
                        # Save the file in its original format
                        with open(file_url, "wb") as f:
                            f.write(file.read())
                        st.success("File has been successfully saved.")

                
                column_names_placeholders = ", ".join(col)
                value_placeholders = ", ".join(["%s"] * len(values))
                
                # Construct  Updated the SQL query
                query = f"INSERT INTO expense ({column_names_placeholders}) VALUES ({value_placeholders})"

                # st.write(query, values)
                cursor.execute(query, tuple(values))
                db.commit()
                st.success("Expense Record Inserted Successfully!")
                st.balloons()

            else:
                st.write("Click above button If you are Sure")
    else:
        st.warning("Please fill up above form")

    df = pd.read_sql('''SELECT * FROM expense''', con=db)
    
    col = select_columns(db)
    show_data(df,col)
    edit_data(cursor, db,col, df,  'Edit Expenses', 'expense')
    delete_data(cursor, db,col, df, 'Delete Expenses', 'expense')


def parameter_listing(cursor, db):
    st.header('🛠️ Parameter Adding')
    with st.form(key='add_parameter_form', clear_on_submit=True, border=True):
        all_data_type = ['VARCHAR(512)', 'double', 
                            'longtext', 'DATE','TIMESTAMP']
        parameter_name = st.text_input('Parameter Name*')
        data_type = st.selectbox('Parameter Types*', all_data_type)
        if st.form_submit_button(label='Submit'):
            if not(parameter_name and data_type):
                st.error('Please fill all the * fields')
            else:
                query = f"ALTER TABLE expense ADD {parameter_name} {data_type}"
                cursor.execute(query)
                db.commit()
                st.success("Parameter Adding Successfully!")
                st.balloons()        