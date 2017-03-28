#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Flask
from flask import abort
from flask import redirect
from flask import render_template
from flask import url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import xlrd
from pdb import set_trace
import os

# 表单类
class NameForm(Form):
    xm = StringField(u'姓名', validators=[DataRequired()])
    zjhm = StringField(u'证件号码(身份证/军官证)', validators=[DataRequired()])
    ksbh = StringField(u'考生编号', validators=[DataRequired()])

    submit = SubmitField(u'查询复试及拟录取情况')

    pass

def toStringValue(cell):
    value = cell.value
    if cell.ctype == xlrd.XL_CELL_NUMBER:
        value = str(long(cell.value))
    return value

# 初始化
def init():
    current_path = os.path.dirname(os.path.realpath(__file__))
    data = xlrd.open_workbook(os.path.join(current_path, 'data.xlsx'))
    table = data.sheets()[0]

    # 读取表头,存在风险:Excel当中表头只能有一行,并且只能是第0行
    header_row = table.row_values(0)
    header = []
    key_xm_index = -1
    key_ksbh_index = -1
    key_zjhm_index = -1
    for i in range(len(header_row)):

        value = header_row[i]

        # 读取姓名\考生编号\证件号码所在的列index,存在风险:如果Excel当中的表头不是这几个汉字,就会找不到
        if value == u'姓名':
            key_xm_index = i
        elif value == u'考生编号':
            key_ksbh_index = i
        elif value == u'证件号码':
            key_zjhm_index = i
        else:
            pass

        header.append(header_row[i])
        pass

    # 写入数据
    for row_index in range(1, table.nrows):
        data_row0 = table.row(row_index)
        data = []
        for i in range(len(header_row)):

            cell = data_row0[i]

            # 把数字转换为Long类型,最终转换成字符串类型
            value = toStringValue(cell)
            data.append(value)
            pass

        xm = toStringValue(data_row0[key_xm_index])
        zjhm = toStringValue(data_row0[key_zjhm_index])
        ksbh = toStringValue(data_row0[key_ksbh_index])

        key = u'%s#%s#%s' % (xm, zjhm, ksbh)

        # print (u'add key :%s' % key)

        ALL_DATA[key] = {
            'header': header,
            'data': data
        }

        pass

    pass


app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guest string'

manager = Manager(app)
bootstrap = Bootstrap(app)

ALL_DATA = dict()
init()


# 错误页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404




@app.route('/', methods=['GET', 'POST'])
def index():

    xm = None
    zjhm = None
    ksbh = None

    form = NameForm()

    if form.validate_on_submit():
        xm = form.xm.data.upper()
        zjhm = form.zjhm.data.upper()
        ksbh = form.ksbh.data.upper()

        form.xm = ''
        form.zjhm = ''
        form.ksbh = ''

        return redirect(url_for('user',
                                xm=xm,
                                zjhm=zjhm,
                                ksbh=ksbh))

    return render_template('index.html',
                           form=form,
                           xm=xm,
                           zjhm=zjhm,
                           ksbh=ksbh)


@app.route('/user/<xm>/<zjhm>/<ksbh>')
def user(xm, zjhm, ksbh):

    key = u'%s#%s#%s' % (xm, zjhm, ksbh)

    if ALL_DATA.has_key(key):
        data0 = ALL_DATA[key]
        return render_template('user.html', data=data0)

    else:
        abort(404)


if __name__ == '__main__':
    #manager.run()
    app.run(host='0.0.0.0', debug=True)

    pass
