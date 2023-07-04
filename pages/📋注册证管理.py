import os
import sqlite3
import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import base64
# import PyPDF2
import numpy as np
# import shutil
import datetime
# from pathlib import Path
import zipfile
from PyPDF2 import PdfReader

from openpyxl.utils.dataframe import dataframe_to_rows
import docx2txt
import plotly.express as px
from st_aggrid import AgGrid
from st_aggrid.shared import GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder



UPLOAD_FOLDER = "uploads"
# 创建数据库连接
def create_connection1():
    conn = sqlite3.connect("file_database.db")
    return conn

#创建数据库
@st.cache_resource
def create_table1():
    conn = create_connection1()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS regmgr
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                mhostnum TEXT,
                product_name TEXT,
                spec_type TEXT,
                factory TEXT,
                price FLOAT,
                regist_number TEXT,
                regist_name TEXT,
                product_type TEXT,
                file_name TEXT,
                file_path TEXT,
                remark1 TEXT,
                record_time TIMESTAMP
                )''')
    conn.commit()
    conn.close()

create_table1()

def save_uploaded_file(uploaded_file,path):
    with open(os.path.join(path, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())

def handle_file_upload():
    uploaded_files = st.file_uploader("附件", accept_multiple_files=True)
    file_details = []
    for uploaded_file in uploaded_files:
        save_uploaded_file(uploaded_file,UPLOAD_FOLDER)
        file_detail = {
            "FileName": uploaded_file.name,
            "FileType": uploaded_file.type,
            "FileSize": uploaded_file.size,
            "file_path": os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        }
        file_details.append(file_detail)
    for file in file_details:
        st.write("成功上传文件:", file['FileName'])
    return file_details
    
        
#记录增删改查
def insert_record(record):
    conn = create_connection1()
    c = conn.cursor()
    c.execute("INSERT INTO regmgr (id,mhostnum, product_name, spec_type, factory, price, regist_number, regist_name, product_type, file_name, file_path, remark1, record_time) VALUES (?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (record['id'],record['mhostnum'], record['product_name'],record['spec_type'] , record['factory'], record['price'], 
               record['regist_number'], record['regist_name'], record['product_type'], record['file_name'], record['file_path'], record['remark1'], record['record_time'],))
    conn.commit()
    conn.close()

def update_record(id, mhostnum, product_name, spec_type, factory, price, regist_number, regist_name, product_type, file_name, file_path, remark1, record_time):
    conn = create_connection1()
    c = conn.cursor()
    c.execute("UPDATE regmgr SET mhostnum=?, product_name=?, spec_type=?, factory=?, price=?, regist_number=?, regist_name=?, product_type=?, file_name=?,file_path=?, remark1=?, record_time=? WHERE id=?",
              (mhostnum, product_name, spec_type, factory, price, regist_number, regist_name, product_type, file_name, file_path, remark1, record_time, id))
    conn.commit()
    conn.close()

def delete_record(id):
    # st.warning("Warning")
    conn = create_connection1()
    c = conn.cursor()
    c.execute("DELETE FROM regmgr WHERE id=?", (id,))
    conn.commit()
    conn.close()

def get_all_records():
    conn = create_connection1()
    c = conn.cursor()
    c.execute("SELECT * FROM regmgr")
    records = c.fetchall()
    conn.close()
    return records

def get_record_by_id(id):
    conn = create_connection1()
    c = conn.cursor()
    c.execute("SELECT * FROM regmgr WHERE id=?", (id,))
    record = c.fetchone()
    conn.close()
    return record

def get_record_by_ids(ids):
    conn = create_connection1()
    c = conn.cursor()
    wstr = ("?, " * len(ids))[:-2]
    # print("this is wstr",wstr)
    query = f"SELECT * FROM regmgr WHERE id IN  ({wstr})"
    params = tuple(ids)
    # print("this is params:",params)
    # d.execute(query,ids)
    c.execute(query, ([str(x) for x in ids]))
    serecords1 = c.fetchall()
    # print("this is serecords1",serecords1)
    conn.commit()
    conn.close()
    return serecords1
#关键词检索功能
def search_records(keyword):
    conn = create_connection1()
    c = conn.cursor()
    # file_title, file_pages, creator, contact, hgroup, file_reciper, file_saver, entry_time, file_summary, file_name, file_path, remarks
    c.execute("SELECT * FROM regmgr WHERE file_name LIKE ? OR file_title LIKE ? OR creator LIKE ?  OR contact LIKE ? OR remarks LIKE ? OR file_summary LIKE ? OR hgroup LIKE ? OR file_reciper LIKE ? OR file_saver LIKE ?",
              (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    records = c.fetchall()
    conn.close()
    return records
#关键词检索功能加日期限定
def search_records_with_date(keyword,start_date,end_date):
    conn = create_connection1()
    c = conn.cursor()
    if keyword:
        # c.execute(f"SELECT * FROM files WHERE file_name LIKE ? OR file_title LIKE ? OR creator LIKE ?  OR contact LIKE ? OR remarks LIKE ? OR file_summary LIKE ? AND strftime('%Y-%m-%d',entry_time) between  strftime('%Y-%m-%d',{start_date}) AND  strftime('%Y-%m-%d',{end_date})",
        #         (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        c.execute("SELECT * FROM regmgr WHERE (file_name LIKE ? OR file_title LIKE ? OR creator LIKE ? OR contact LIKE ? OR remarks LIKE ? OR file_summary LIKE ? OR hgroup LIKE ? OR file_reciper LIKE ? OR file_saver LIKE ?) AND strftime('%Y-%m-%d', entry_time) BETWEEN ? AND ?",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    else:
        # c.execute(f"SELECT * FROM files WHERE strftime('%Y-%m-%d',entry_time) between strftime('%Y-%m-%d',{start_date}) AND strftime('%Y-%m-%d',{end_date})")
        c.execute("SELECT * FROM regmgr WHERE  strftime('%Y-%m-%d', entry_time) BETWEEN ? AND ?",
            (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    records = c.fetchall()
    conn.close()
    return records
#预览附件
def display_file(file_path):
    file_type = file_path.split(".")[-1].lower()
    # print (file_type)

    if file_type in ["jpg", "jpeg", "png","PNG"]:
        image = Image.open(file_path)
        st.image(image, caption=file_path, use_column_width=True)
    elif file_type in ["zip"]:
        with zipfile.ZipFile(file_path, "r") as z:
            st.write("Zip Content:")
            for f in z.namelist():
                st.write(f)
    elif file_type in ["pdf", "PDF"]:
        try:
            pdf = PdfReader(file_path, "rb")
            page = pdf.pages[1] 
            text = page.extract_text()
            st.write(text)
        except:
            st.warning("预览的PDF文档不能为扫描件！！")
        

    elif file_type in ["txt", "TXT","csv","CSV"]:
        with open(file_path, "rb") as f:
            text = str(f.read(),"utf-8")
            st.write(text)
            f.close()
    elif file_type in ["doc", "docx"]:
        docx_text = docx2txt.process(file_path)
        st.write(docx_text)
                    
    else:
        st.write("Unsupported file format.")

#记录导出功能
def export_records(records):
    datestr = datetime.datetime.now()
    date_str = datestr.strftime('%Y_%m_%d')
    # expfilpth = f"downloads\记录{date_str}.xlsx"

    df = pd.DataFrame(records, columns=["id", "文件标题","文件总页数","文件上报人","上报人联系方式","所属组", "文件接收人",  "文件保管人", "审批完成日期", "文件摘要", "文件名", "文件存储路径","备注"])
    df.to_excel(f"downloads\记录{date_str}.xlsx", index=False)
    # return expfilpth
#导出选中的记录功能
def export_selected_records(records):
    serecords = get_record_by_ids(records)
    # print(serecords) 
    datestr = datetime.datetime.now()
    date_str = datestr.strftime('%Y_%m_%d')
    # expfilpth = f"downloads\记录{date_str}.xlsx"
    df = pd.DataFrame(serecords, columns=["id", "文件标题","文件总页数","文件上报人","上报人联系方式","所属组", "文件接收人",  "文件保管人", "审批完成日期", "文件摘要", "文件名", "文件存储路径","备注"])
    df.to_excel(f"downloads\记录{date_str}.xlsx", index=False)    

def get_image_download_link(img, filename):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/jpeg;base64,{img_str}" download="{filename}" target="_blank">点击下载图片</a>'
    return href
    
st.title("文件信息系统系统")
#侧边栏
st.sidebar.header("医工科注册证管理系统")
mode = st.sidebar.selectbox("注册证管理", ["新增记录", "查看记录", "修改记录"])
st.image("./banner1.png",use_column_width='always')
# 上传文件
############################################# 第一页 ############################################
if mode == "新增记录":
    st.header("🏢新增记录✍")
    records = get_all_records()
    # df = pd.DataFrame(records,columns=["id", "总医院序号","产品名称","规格型号","生产厂家","产品价格", "注册证号",  "注册证名称", "产品类型","附件名", "附件存放地址", "备注", "记录创建时间"])
    df = pd.DataFrame(records,columns=["id", "mhostnum", "product_name", "spec_type", "factory", "price", "regist_number", "regist_name", "product_type", "file_name", "file_path", "remark1", "record_time"])
    # df = df.fillna('None')
    if len(df)>1:
        maxid = df.iat[-1,0]
    else:
        maxid = 0
    # print(a)
    idx = int(maxid) + 1

    filedetails = handle_file_upload()
    if filedetails:
        filenames = [d['FileName'] for d in filedetails]
        filepaths = [d['file_path'] for d in filedetails]
    else:
        filenames = ["",""]
        filepaths = ["",""]

    # st.header("添加记录")

    mhostnum = st.text_input("总医院序号")
    product_name = st.text_input("产品名称")
    spec_type = st.text_input("规格型号")
    factory = st.text_input("生产厂家")
    price = st.number_input("产品价格", min_value=0, value=0, step=1)
    regist_number = st.text_input("注册证号")
    regist_name = st.text_input("注册证名称")
    product_type = st.text_input("产品类型")
    remark1 = st.text_input("备注")
    entry_time = st.date_input("记录创建时间",value=datetime.datetime.now())


    if st.button("保存记录"):
        record = {
            "id": idx,
            "mhostnum": mhostnum,
            "product_name": product_name,
            "spec_type": spec_type,
            "factory": factory,
            "price":price,
            "regist_number":regist_number,
            "regist_name":regist_name,
            "product_type": product_type,
            "file_name": filenames[0],
            "file_path": filepaths[0],
            "remark1":remark1,
            "record_time": entry_time         
        }
        if record["product_name"] and record["price"] is not None:
            insert_record(record)
            st.success("记录已保存")
            st.empty()
        else:
            st.warning("产品名和产品价格不能为空！！")

######################################### 第二页 ##########################################
# 显示记录
if mode == "查看记录":  
    st.header("查看记录")          
    records = get_all_records()
    df = pd.DataFrame(records,columns=["id", "总医院序号","产品名称","规格型号","生产厂家","产品价格", "注册证号",  "注册证名称", "产品类型","附件名", "附件存放地址", "备注", "记录创建时间"])
    # df = pd.DataFrame(records,columns=["id", "mhostnum", "product_name", "spec_type", "factory", "price", "regist_number", "regist_name", "product_type", "file_name", "file_path", "remark1", "record_time"])
    df = df.fillna('None')
    
    index = len(df)
    # Initiate the streamlit-aggrid widget
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_side_bar()
    gb.configure_default_column(groupable=True, value=True,
    enableRowGroup=True, aggFunc="sum",editable=True)
    gb.configure_selection(selection_mode="multiple",use_checkbox=False)
    gridOptions = gb.build()
    # Insert the dataframe into the widget
    df_new = AgGrid(df,gridOptions=gridOptions,enable_enterprise_modules=True, 
                    update_mode=GridUpdateMode.MODEL_CHANGED, enable_quicksearch=True,excel_export_mode="MANUAL")
    
    # if st.button('-----------新增记录-----------'):
    #     conn = create_connection1()
    #     df_new['data'].loc[index,:] = 'None'
    #     # new_cloumns = ["mhostnum", "product_name", "spec_type", "factory", "price", "regist_number", "regist_name", "product_type", "file_name", "file_path", "remark1", "record_time"]
    #     # df_new = df_new.reindex(columns=new_cloumns)
    #     df_new['data'].to_sql(name='regmgr', con=conn, if_exists='replace', index=False,chunksize=1000)
    #     st.experimental_rerun()
    #     # Save the dataframe to disk if the widget has been modified
    # if df.equals(df_new['data']) is False:
    #     conn = create_connection1()
    #     # new_cloumns = ["mhostnum", "product_name", "spec_type", "factory", "price", "regist_number", "regist_name", "product_type", "file_name", "file_path", "remark1", "record_time"]
    #     # df_new = df_new.reindex(columns=new_cloumns)
    #     df_new['data'].to_sql(name='regmgr', con=conn, if_exists='replace', index=False,chunksize=1000)
    #     st.experimental_rerun()  
    # if st.button('-----------删除记录-----------'):
    #     if len(df_new['selected_rows']) > 0:
    #         conn = create_connection1()
    #         exclude = pd.DataFrame(df_new['selected_rows'])
    #         print(exclude)
    #         # pd.merge(df_new['data'], exclude, how='outer',
    #         # indicator=True).query('_merge == "left_only"').drop('_merge', axis=1).to_sql(name='mytable', con=conn, if_exists='replace', index=False)
    #         st.experimental_rerun()
    #     else:
    #         st.warning('请至少选择一条记录')
        # # Check for duplicate rows
        # if df_new['data'].duplicated().sum() > 0:
        #     st.warning('**重复的记录:** %s' % (df_new['data'].duplicated().sum()))
        # if st.button('-----------删除重复-----------'):
        #     df_new['data'] = df_new['data'].drop_duplicates()
        #     df_new['data'].to_csv(path,index=False)
        #     st.experimental_rerun()    

######################################### 第三页 ##########################################
# 显示记录
if mode == "修改记录":  
    st.header("修改记录")          
    records = get_all_records()
    # df = pd.DataFrame(records,columns=["id", "总医院序号","产品名称","规格型号","生产厂家","产品价格", "注册证号",  "注册证名称", "产品类型","附件名", "附件存放地址", "备注", "记录创建时间"])
    df = pd.DataFrame(records,columns=["id", "mhostnum", "product_name", "spec_type", "factory", "price", "regist_number", "regist_name", "product_type", "file_name", "file_path", "remark1", "record_time"])
    rennames = {"id":"id", "mhostnum":"总医院序号", "product_name":"产品名称", "spec_type":"规格型号", "factory":"生产厂家",
                "price":"产品价格", "regist_number":"注册证号", "regist_name":"注册证名称", "product_type":"产品类型", 
                "file_name":"附件名", "file_path":"附件存放地址", "remark1":"备注", "record_time":"记录创建时间"}
    # df = df.fillna('None')
    df = df.rename(columns=rennames)
    index = len(df)
    # Initiate the streamlit-aggrid widget
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_side_bar()
    gb.configure_default_column(groupable=True, value=True,
    enableRowGroup=True, aggFunc="sum",editable=True)
    gb.configure_selection(selection_mode="multiple",use_checkbox=True)
    
    gridOptions = gb.build()
    # gridOptions.defaultLanguage = 'zh-cn';
    # Insert the dataframe into the widget
    df_new = AgGrid(df,gridOptions=gridOptions,enable_enterprise_modules=True, 
                    update_mode=GridUpdateMode.MODEL_CHANGED, enable_quicksearch=True,excel_export_mode="MANUAL")
    cl1, cl2 = st.columns([0.2,0.2])
    with cl1:
        if st.button('-----------新增记录-----------'):
            conn = create_connection1()
            df_new['data'].loc[index,:] = 'None'
            # new_cloumns = ["mhostnum", "product_name", "spec_type", "factory", "price", "regist_number", "regist_name", "product_type", "file_name", "file_path", "remark1", "record_time"]
            # df_new = df_new.reindex(columns=new_cloumns)
            df_new['data'].to_sql(name='regmgr', con=conn, if_exists='replace', index=False,chunksize=1000)
            st.experimental_rerun()
            # Save the dataframe to disk if the widget has been modified
        if df.equals(df_new['data']) is False:
            conn = create_connection1()
            # new_cloumns = ["mhostnum", "product_name", "spec_type", "factory", "price", "regist_number", "regist_name", "product_type", "file_name", "file_path", "remark1", "record_time"]
            # df_new = df_new.reindex(columns=new_cloumns)
            df_new['data'].to_sql(name='regmgr', con=conn, if_exists='replace', index=False,chunksize=1000)
            st.experimental_rerun()  
        if st.button('-----------删除记录-----------'):
            if len(df_new['selected_rows']) > 0:
                # conn = create_connection1()
                exclude = pd.DataFrame(df_new['selected_rows'])
                [ delete_record(i) for i in exclude['id'] ]
                st.success("删除成功")
                st.balloons
                # pd.merge(df_new['data'], exclude, how='outer',
                # indicator=True).query('_merge == "left_only"').drop('_merge', axis=1).to_sql(name='mytable', con=conn, if_exists='replace', index=False)
                st.experimental_rerun()
            else:
                st.warning('请至少选择一条记录')
            # # Check for duplicate rows
            # if df_new['data'].duplicated().sum() > 0:
            #     st.warning('**重复的记录:** %s' % (df_new['data'].duplicated().sum()))
            # if st.button('-----------删除重复-----------'):
            #     df_new['data'] = df_new['data'].drop_duplicates()
            #     df_new['data'].to_csv(path,index=False)
            #     st.experimental_rerun()    
    file_path = ''
    with cl2:
        if st.button('-----------预览附件-----------'):
            if len(df_new['selected_rows']) == 1:
                selects = pd.DataFrame(df_new['selected_rows'])
                id = int(selects['id'][0])
                # print(id)
                file_path = get_record_by_id(id)[-3]
                file_path = os.path.join(os.getcwd(), file_path)
            else:
                st.warning('**请选择一条记录进行预览**')
    if file_path:
        display_file(str(file_path))                
    with cl2:
        if len(df_new['selected_rows']) == 1:
            selects = pd.DataFrame(df_new['selected_rows'])
            id = int(selects['id'][0])
            filpth = get_record_by_id(id)[-3]
            if filpth:
                filpth = r'{}'.format(filpth)
                filna = filpth.split('\\')[1]
                down_btn = st.download_button(
                        label="-----------下载附件-----------",
                        data=open(filpth, "rb"),
                        file_name=filna
                        )
        elif len(df_new['selected_rows']) > 1 and st.button(label="-----------下载附件-----------"):
            st.warning('**请选择一条记录进行下载！！**')
            
# #从excel中导入记录    
# # 定义函数，用于将Excel中的数据插入到数据库中
#     file_type = file_path.split(".")[-1].lower()
#     # print (file_type)

#     if file_type in ["jpg", "jpeg", "png","PNG"]:
#         image = Image.open(file_path)
#         st.image(image, caption=file_path, use_column_width=True)
# def insert_data():
#     filedetails = handle_file_upload()
#     file_paths = np.nan
#     if filedetails:
#         file_names = [d['file_name'] for d in filedetails]
#     # print(file_path)
#     if not file_names:
#         st.warning("错误，请选择一个需要导入的excel文件！")
#         return
#     file_path = os.path.join(os.getcwd(),file_names[0])
#     try:
#         # 读取Excel文件
#         df = pd.read_excel(file_path)
#         # 将空值替换为None
#         df = df.where(pd.notnull(df), None)
#         # 只保留需要插入的字段
#         df = df[['device_type_id','tenant_code','device_type','device_name', 'company_code', 'product_no', 'iccid', 'sim_card_no', 'remark', 'create_time', 'imei']]
#         # 将数据转化为元组的列表
#         data = [tuple(x) for x in df.to_records(index=False)]
#         # 插入数据
#         sql = "INSERT INTO device_info (device_type_id,tenant_code,device_type,device_name, company_code, product_no, iccid, sim_card_no, remark, create_time, imei) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s)"
#         cursor.executemany(sql, data)
#         db.commit()
#         messagebox.showinfo("插入成功", "已成功将数据插入到数据库中！")
#     except Exception as e:
#         db.rollback()
#         messagebox.showerror("插入失败", "插入数据时出现错误：" + str(e))

# # 定义函数，用于将Excel中的数据更新到数据库中
# def update_data():
#     file_path = file_entry.get()
#     if not file_path:
#         messagebox.showerror("错误", "请选择要导入的Excel文件！")
#         return
#     try:
#         # 读取Excel文件
#         df = pd.read_excel(file_path)
#         # 将空值替换为None
#         df = df.where(pd.notnull(df), None)
#         # 只保留需要更新的字段
#         df = df[['device_type_id','tenant_code','device_type','device_name', 'company_code', 'product_no', 'iccid', 'sim_card_no', 'create_time', 'imei']]
#         for index, row in df.iterrows():
#             # 查询数据库中是否存在该imei对应的记录
#             sql = "SELECT * FROM device_info WHERE imei=%s"
#             cursor.execute(sql, (row['imei'],))
#             result = cursor.fetchone()
#             if result:
#                 # 如果存在，就更新记录
#                 sql = "UPDATE device_info SET device_type_id=%s,tenant_code=%s,device_type=%s, device_name=%s, company_code=%s, product_no=%s, iccid=%s, sim_card_no=%s, create_time=%s WHERE imei=%s"
#                 cursor.execute(sql, (row['device_type_id'],row['tenant_code'],row['device_type'],row['device_name'], row['company_code'], row['product_no'], row['iccid'], row['sim_card_no'], row['create_time'], row['imei']))
#             else:
#                 # 如果不存在，就插入新记录
#                 sql = "INSERT INTO device_info (device_type_id,tenant_code,device_type,device_name, company_code, product_no, iccid ,sim_card_no, create_time, imei) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
#                 cursor.execute(sql, (row['device_type_id'],row['tenant_code'],row['device_type'],row['device_name'], row['company_code'], row['product_no'], row['iccid'], row['sim_card_no'], row['create_time'], row['imei']))
#         db.commit()
#         messagebox.showinfo("更新成功", "已成功将数据更新到数据库中！")
#     except Exception as e:
#         db.rollback()
#         messagebox.showerror("更新失败", "更新数据时出现错误：" + str(e))        