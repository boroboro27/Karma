import random
from flask import Flask
from flask_mail  import Mail, Message
from flask import flash, redirect, render_template, request, session, url_for, abort
import pymssql
from smtplib import SMTPException


# создание экземпляра приложения
app = Flask(__name__)

# подключение настроек приложения из файла
app.config.from_object('config.DevelopementConfig')

# инициализирует расширения
mail = Mail(app)

def callproc(proc: str, params: tuple) -> dict:
  with pymssql.connect('T2RU-SSCSAND-01', 'User_SSC_BC', 'sscbc27', 'DB_SSC_BC') as conn:
      with conn.cursor(as_dict=True) as cursor: 
          cursor.callproc(proc, params)          
          res_dict = [*cursor]
          conn.commit()
          return res_dict

def send_email(subject: str, body: str, users: list[str]) -> tuple[bool, str | None]:
    """
        Отправляет письмо на адреса электронной почты пользователей

        :param: subject: заголовок письма, body: текст письма, users: список адресов эл. почты
        :return: кортеж с информацией о статусе отправки письма (true/false и описание ошибки(при наличии))
        """
    try:
        with mail.connect() as conn:
            for user in users:
                msg = Message(recipients=[user],
                              body=body,
                              subject=subject)

                conn.send(msg)
            #app.logger.info(f'Письмо с темой "{subject}" отправлено пользователю {user}')
            return (True, )
    except SMTPException as err:
        return (False, str(err))  


@app.route("/", methods=["POST", "GET"])
def index():
    if 'logged_in' in session:
        if request.method == "POST":
            pass
        else:
            return render_template('index.html', title='Каталог "Книжного перекрестка"',
                                   avl_books=callproc('[dbo].[sp_get_available_books]', (session['userLogged'],)),                                   
                                   taken_books=callproc('[dbo].[sp_get_taken_books]', (session['userLogged'],)),
                                   menu=callproc('[dbo].[sp_get_menu]', ()), user=session['userLogged'].split('@')[0])
    else:
        return redirect(url_for('login'))
    
@app.route("/about")
def about():
    if 'logged_in' in session:
        
        return render_template('about.html', title='О проекте "Книжный перекресток"', menu=callproc('[dbo].[sp_get_menu]', ()),
                               user=session['userLogged'].split('@')[0])
    else:
        return redirect(url_for('login'))


@app.route("/add_book", methods=["POST", "GET"])
def add_book():
    
    if 'logged_in' in session:        
        if request.method == "POST":
            # title, author, year, status, add_userid
            res = callproc('[dbo].[sp_add_new_book]', (session['userLogged'], 
                                            request.form["title-book"].strip(),
                                            request.form["author-book"].strip(),
                                            request.form["genre_id"].strip(),
                                            request.form["year-book"].strip(),
                                            request.form["pages"].strip()
                                            ))            
            if not res[0]['result']:
                flash(f"Ошибка добавления книги в каталог. Если не удается устранить ошибку самостоятельно, \n"
                      f"сообщите, пожалуйста, нам об ошибке через форму обратной связи.", category='error')
            else:                
                flash((f"Книга успешно добавлена в каталог под номером #{res[0]['result']}. \n"                       
                       f"Запишите этот номер в книгу на 17ой странице. \n"
                       f'Благодаря этому любой читатель книги всегда будет знать, кому она принадлежит. \n'
                       f"Спасибо, что поддерживаете активность в нашем проекте."), category='success')

        return render_template('add-book.html', title="Регистрация новой книги",
                               menu=callproc('[dbo].[sp_get_menu]', ()), genres=callproc('[dbo].[sp_get_genres]', ()),
                               user=session['userLogged'].split('@')[0])
    else:
        return redirect(url_for('login'))

@app.route('/req_take_book/<string:book_code>', methods=["GET"])
def req_take_book(book_code):    
    if 'logged_in' in session:   
        res = callproc('[dbo].[sp_change_status]', (book_code, 2, session['userLogged']))
        if not res[0]['result']:
            flash(f"Ошибка при запросе книги с кодом #{book_code} у владельца. \n"
                  f"Убедитесь, что у вас нет на руках других книг, или что вы являетесь владельцем этой книги. \n"
                  f"Кроме этого, возможно, что книга уже выдана или запрошена другим пользователем :) \n"
                  f"Если не удается выявить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Книга с кодом #{book_code} успешно запрошена у владельца. \n"
                   f"Мы сообщили ему об этом по эл. почте. \n"
                    f'Ожидайте, пожалуйста, когда владелец свяжется с вами для передачи книги.'), category='success')    
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))
    
@app.route('/unreq_take_book/<string:book_code>', methods=["GET"])
def unreq_take_book(book_code):    
    if 'logged_in' in session:   
        res = callproc('[dbo].[sp_change_status]', (book_code, 3, session['userLogged']))
        if not res[0]['result']:
            flash(f"Ошибка при отмене запроса к владельцу на выдачу книги с кодом #{book_code}. \n"                  
                  f"Если не удается выявить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Отменен запрос на выдачу книги с кодом #{book_code}. "
                    f'Владелец книги будет уведомлен об этом по эл. почте. '), category='success')    
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))


@app.route('/take_book/<string:book_code>/<string:reader>', methods=["GET"])
def take_book(book_code, reader):    
    if 'logged_in' in session:        
        res = callproc('[dbo].[sp_change_status]', (book_code, 4, session['userLogged']))        
        if not res[0]['result']:
            flash(f"Ошибка при выдаче книги под номером #{book_code}. \n"
                  f"Если не удается устранить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Книга под номером #{book_code} успешно выдана читателю. \n"
                    f"Спасибо, что поддерживаете активность в нашем проекте."), category='success')
        
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))
    
@app.route('/req_extend_book/<string:book_code>', methods=["GET"])
def req_extend_book(book_code):    
    if 'logged_in' in session:   
        res = callproc('[dbo].[sp_change_status]', (book_code, 5, session['userLogged']))
        if not res[0]['result']:
            flash(f"Ошибка при запросе на продление книги с кодом #{book_code} у владельца. \n"                  
                  f"Если не удается выявить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Книга с кодом #{book_code}: успешно запрошено продление у владельца. \n"
                   f"Мы сообщили ему об этом по эл. почте. \n"
                    f'Ожидайте, пожалуйста, когда владелец примет решение о продлении книги или об отказе в продлении.'), category='success')    
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))
    

    
@app.route('/unreq_extend_book/<string:book_code>', methods=["GET"])
def unreq_extend_book(book_code):    
    if 'logged_in' in session:   
        res = callproc('[dbo].[sp_change_status]', (book_code, 6, session['userLogged']))
        if not res[0]['result']:
            flash(f"Ошибка при отмене запроса к владельцу на продление книги с кодом #{book_code}. \n"                  
                  f"Если не удается выявить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Отменен запрос на продление книги с кодом #{book_code}. \n"
                    f'Владелец книги будет уведомлен об этом по эл. почте. '), category='success')    
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))
    

@app.route('/extend_book/<string:book_code>/<string:reader>', methods=["GET"])
def extend_book(book_code, reader):    
    if 'logged_in' in session:        
        res = callproc('[dbo].[sp_change_status]', (book_code, 7, session['userLogged']))        
        if not res[0]['result']:
            flash(f"Ошибка при подтверждении продления книги под номером #{book_code}. \n"
                  f"Если не удается устранить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Книга под номером #{book_code} успешно продлена. \n"
                   f'Читатель книги будет уведомлен об этом по эл. почте.\n'
                   f"Спасибо, что поддерживаете активность в нашем проекте. \n"), category='success')
        
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))
    
@app.route('/unextend_book/<string:book_code>/<string:reader>', methods=["GET"])
def unextend_book(book_code, reader):    
    if 'logged_in' in session:        
        res = callproc('[dbo].[sp_change_status]', (book_code, 8, session['userLogged']))        
        if not res[0]['result']:
            flash(f"Ошибка при отказе в продлении книги под номером #{book_code}. \n"
                  f"Если не удается устранить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Читателю отказано в продлении книги под номером #{book_code}. \n"
                   f'Читатель книги будет уведомлен об этом по эл. почте.\n'
                   f"Мы с пониманием относимся к вашему решению и знаем, что вы взвесили все за и против:)\n"), 
                   category='success')
        
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))
    
@app.route('/req_return_book/<string:book_code>', methods=["GET"])
def req_return_book(book_code):    
    if 'logged_in' in session:   
        res = callproc('[dbo].[sp_change_status]', (book_code, 9, session['userLogged']))
        if not res[0]['result']:
            flash(f"Ошибка при запросе к владельцу на возврат книги с кодом #{book_code}. \n"                  
                  f"Если не удается выявить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Книга с кодом #{book_code}: успешно запрошен возврат книги владельцу. \n"
                   f"Мы сообщили ему об этом по эл. почте. \n"
                    f'Ожидайте, пожалуйста, когда владелец свяжется с вами для передачи ему книги'), category='success')    
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))
    
@app.route('/unreq_return_book/<string:book_code>', methods=["GET"])
def unreq_return_book(book_code):    
    if 'logged_in' in session:   
        res = callproc('[dbo].[sp_change_status]', (book_code, 10, session['userLogged']))
        if not res[0]['result']:
            flash(f"Ошибка при отмене запроса к владельцу на возврат книги с кодом #{book_code}. \n"                  
                  f"Если не удается выявить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Отменен запрос на возврат книги с кодом #{book_code}. \n"
                    f'Владелец книги будет уведомлен об этом по эл. почте. '), category='success')    
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))


@app.route('/return_book/<string:book_code>/<string:reader>', methods=["GET"])
def return_book(book_code, reader):    
    if 'logged_in' in session:        
        res = callproc('[dbo].[sp_change_status]', (book_code, 11, session['userLogged']))        
        if not res[0]['result']:
            flash(f"Ошибка при подтверждении возврата владельцу книги под номером #{book_code}. \n"
                  f"Если не удается устранить ошибку самостоятельно, \n"
                    f"сообщите, пожалуйста, нам об этом через форму обратной связи.", category='error')
        else:
            flash((f"Книга под номером #{book_code} успешно позвращена владельцу. \n"                   
                   f"Спасибо, что поддерживаете активность в нашем проекте. \n"), category='success')
        
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))


@app.route('/subscribe_book/<string:book_code>', methods=["GET"])
def subscribe_book(book_code):
    if 'logged_in' in session:
        res = callproc('[dbo].[[sp_add_new_subscription]]', (book_code, session['userLogged']))  
        if not res[0]['result']:
            flash(f"Ошибка при подписке на книгу с кодом #{book_code}. \nЕсли не удается устранить ошибку самостоятельно, \n"
                  f"сообщите, пожалуйста, нам об ошибке через форму обратной связи.", category='error')
        else:
            msg = (f"Оформлена новая подписка на книгу с кодом #{book_code}. \n"
                   f'Теперь мы будем сообщать вам, если книга возвращается владельцу и снова доступна для выдачи.')            

        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))


@app.route('/unsubscribe_book/<string:book_code>', methods=["GET"])
def unsubscribe_book(book_code):
    if 'logged_in' in session:
        res = callproc('[dbo].[[sp_add_new_subscription]]', (book_code, session['userLogged']))  
        if not res[0]['result']:
            flash(f"Ошибка при отмене подписки на книгу с кодом #{book_code}. \n"
                  f"Если не удается устранить ошибку самостоятельно, \n"
                  f"сообщите, пожалуйста, нам об ошибке через форму обратной связи.", category='error')
        else:
            flash((f"Подписка на книгу с кодом #{book_code} прекращена. \n"
                   f"Теперь мы НЕ будем сообщать вам, если книга возвращается владельцу и снова доступна для выдачи."), 
                   category='success')

        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))


@app.route("/rules", methods=["GET"])
def rules():
    if 'logged_in' in session:
        
        return render_template('rules.html', title='Правила проекта "Книжный перекрёсток"',
                               rules=callproc('[dbo].[sp_get_rules]', ()),
                               menu=callproc('[dbo].[sp_get_menu]', ()),
                               user=session['userLogged'].split('@')[0])
    else:
        return redirect(url_for('login'))


@app.route("/lk", methods=["POST", "GET"])
def lk():
    if 'logged_in' in session:
        
        user_id = dbase.getUser(session['userLogged'])
        return render_template('lk.html', title='Личный кабинет',
                               # True - т.е. для отображения в ЛК, а не на главной
                               taken_books=callproc('[dbo].[sp_get_taken2me_books]', (session['userLogged'],)),
                               subscriptions=dbase.getSubscriptions(
                                   user_id[0]),
                               book_log=dbase.getBookLog(user_id[0]),
                               menu=callproc('[dbo].[sp_get_menu]', ()),
                               user=session['userLogged'].split('@')[0], user_id=user_id[0])
    else:
        return redirect(url_for('login'))

# для ввода кода подтверждения отправляй код на почту
# и перенаправляй на спец страницу с формой для ввода полученного кода


@app.route("/login", methods=["POST", "GET"])
def login():
    if 'logged_in' in session:
        return redirect(url_for('rules'))

    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        if email.split('@')[1] == 'tele2.ru':
            session['userLogged'] = email            
            code = random.randint(1000, 9999)  # генерация случайного кода
            session['code'] = code  # сохранение кода в сессии
            is_sent = send_email('Код подтверждения',
                               f'Ваш код подтверждения: {code}',
                               [email])
            if not is_sent[0]:
                flash(f"Ошибка при отправке кода подтверждения: {is_sent[1]}. Если не удается устранить ошибку самостоятельно, \n"
                      f"обратитесь, пожалуйста, к организаторам проекта Книжный перекресток.", category='error')
                return redirect(url_for('login'))
            else:
                flash(f"Код подтверждения успешно отправлен на адрес электронной почты {email}. "
                      f"Проверьте вашу почту и введите полученный код в поле ниже.", category='success')
                return render_template('verify_code.html', title="Ввод кода подтверждения", menu=callproc('[dbo].[sp_get_menu]', ()))
        else:
            flash(f"Не верно указан адрес корпоративной электронной почты (ххх@tele2.ru). Если не удается устранить ошибку самостоятельно, \n"
                  f"обратитесь, пожалуйста, к организаторам проекта Книжный перекресток.", category='error')
            return redirect(url_for('login'))
    else:
        return render_template('login.html', title="Авторизация участника", menu=callproc('[dbo].[sp_get_menu]', ()))

# обработка ввода кода подтверждения
@app.route('/verify_code', methods=["POST", "GET"])
def verify_code():
    if 'logged_in' in session:
        return redirect(url_for('rules'))
        
    if request.method == 'POST':
        code = request.form['code']
        if 'code' in session and str(session['code']) == code:
            add_user = callproc('[dbo].[sp_add_new_user]', (session['userLogged'],))
            #Если 1, то новый пользователь добавлен, если 0 - уже зарегистрирован
            if add_user[0]['result']: 
                # сохранение информации о входе в сессию
                session['logged_in'] = True
                return redirect(url_for('rules'))
            else:
                # сохранение информации о входе в сессию
                session['logged_in'] = True
                return redirect(url_for('index'))        
        else:
            flash(f"Код подтверждения указан не верно. Попробуйте ввести повторно. "
                  f"Если не удается устранить ошибку самостоятельно, "
                  f"обратитесь, пожалуйста, к организаторам проекта.",
                  category='error')
            return redirect(url_for('verify_code'))
    else:
        return render_template('verify_code.html', title="Ввод кода подтверждения", menu=callproc('[dbo].[sp_get_menu]', ()))


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if 'logged_in' in session:
        user_id = dbase.getUser(session['userLogged'])
        if request.method == "POST":
            msg = request.form['message'].strip()
            res = dbase.addFeedback(msg, user_id[0])
            if not res[0]:
                flash(
                    f"Ошибка отправки обращения: {res[1]}.", category='error')
            else:
                flash((f"Обращение #{res[1]} принято в работу. "
                       f"Ожидайте ответа на адрес вашей эл. почты {session['userLogged']}"), category='success')

        return render_template('contact.html', title="Обратная связь", menu=callproc('[dbo].[sp_get_menu]', ()),
                               feedbacks=dbase.getAllFeedbacks(), user=session['userLogged'].split('@')[0],
                               is_admin=user_id[1])
    else:
        return redirect(url_for('login'))


@app.route('/close_feedback/<int:fb_id>', methods=["GET"])
def close_feedback(fb_id):
    if 'logged_in' in session:
        user_id = dbase.getUser(session['userLogged'])
        if user_id[1] != 1:
            return redirect(url_for('contact'))

        res = dbase.closeFeedback(fb_id)
        if not res[0]:
            flash(
                f"Ошибка при закрытии обращения #{fb_id}: {res[1]}.", category='error')
        else:
            flash(
                (f'Обращение #{fb_id} закрыто (закрыто обращений в БД: {res[1]})'), category='success')

        return redirect(url_for('contact'))
    else:
        return redirect(url_for('login'))


@app.route("/exit", methods=["GET"])
def exit():
    session.clear()
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Страница не найдена', menu=callproc('[dbo].[sp_get_menu]', ())), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template('page403.html', title='Доступ к информации ограничен, т.к. вы не являетесь администратором ресурса.',
                           menu=callproc('[dbo].[sp_get_menu]', ())), 403

if __name__ == "__main__":
    app.run(host='0.0.0.0')