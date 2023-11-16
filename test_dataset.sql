EXEC	[dbo].[sp_add_new_user]
		@user_email = N'ruslan.borodin@tele2.ru'

EXEC	[dbo].[sp_add_new_user]
		@user_email = N'natalya.korzon@tele2.ru'

EXEC	[dbo].[sp_add_new_user]
		@user_email = N'nikolay.korostelev@tele2.ru'

EXEC	[dbo].[sp_get_available_books]
		@user_email = N'ruslan.borodin@tele2.ru'

EXEC	[dbo].[sp_get_available_books]
		@user_email = N'natalya.korzon@tele2.ru'

		---успешно
EXEC	[dbo].[sp_change_status]
		@book_code = N'145810',
		@oper_id = 2,
		@user_email = N'ruslan.borodin@tele2.ru'

		---НЕуспешно
EXEC	[dbo].[sp_change_status]
		@book_code = N'111435',
		@oper_id = 2,
		@user_email = N'ruslan.borodin@tele2.ru'

		---успешно
EXEC	[dbo].[sp_change_status]
		@book_code = N'711435',
		@oper_id = 2,
		@user_email = N'natalya.korzon@tele2.ru'

		---НЕуспешно
EXEC	[dbo].[sp_change_status]
		@book_code = N'958105',
		@oper_id = 2,
		@user_email = N'natalya.korzon@tele2.ru'

EXEC	[dbo].[sp_change_status]
		@book_code = N'563607',
		@oper_id = 2,
		@user_email = N'ruslan.borodin@tele2.ru'

EXEC	[dbo].[sp_change_status]
		@book_code = N'145810',
		@oper_id = 3,
		@user_email = N'ruslan.borodin@tele2.ru'

EXEC	[dbo].[sp_change_status]
		@book_code = N'569787',
		@oper_id = 4,
		@user_email = N'ruslan.borodin@tele2.ru'

EXEC	[dbo].[sp_get_taken_books]
		@user_email = N'natalya.korzon@tele2.ru'

EXEC	[dbo].[sp_get_taken_books]
		@user_email = N'ruslan.borodin@tele2.ru'

		---успешно
EXEC	[dbo].[sp_change_status]
		@book_code = N'958105',
		@oper_id = 2,
		@user_email = N'nikolay.korostelev@tele2.ru'

		---успешно
EXEC	[dbo].[sp_change_status]
		@book_code = N'958105',
		@oper_id = 4,
		@user_email = N'ruslan.borodin@tele2.ru'

EXEC	[dbo].[sp_change_status]
		@book_code = N'958105',
		@oper_id = 2,
		@user_email = N'nikolay.korostelev@tele2.ru'