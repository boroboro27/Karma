EXEC	[dbo].[sp_add_new_user]
		@user_email = N'ruslan.borodin@tele2.ru'

EXEC	[dbo].[sp_add_new_user]
		@user_email = N'natalya.korzon@tele2.ru'

EXEC	@return_value = [dbo].[sp_add_new_book]
		@user_email = N'ruslan.borodin@tele2.ru',
		@title = N'Любовь к трем цукербринам',
		@author = N'Виктор Пелевин',
		@genre_id = 1,
		@public_year = 2014

