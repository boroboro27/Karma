USE [DB_SSC_BC]
GO
/****** Object:  StoredProcedure [dbo].[sp_add_new_book]    Script Date: 07.11.2023 17:46:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Руслан Бородин
-- Create date: 07.11.2023
-- Description:	Запрос на выдачу свободной книги
-- =============================================
ALTER PROCEDURE [dbo].[sp_request_take]
	-- Add the parameters for the stored procedure here
	@user_email varchar(50), @book_code varchar(50)
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

   DECLARE @user_id BIGINT, @book_id BIGINT

	EXEC [dbo].[sp_get_user] @user_email = @user_email, @user_id = @user_id OUTPUT 
	EXEC [dbo].[sp_get_book] @book_code = @book_code, @book_id = @book_id OUTPUT

   --Проверяем, что кто-то уже ранее не сделал активный запрос на выдачу этой книги
   IF Not Exists ( Select Top 1 *
		From forms With ( NoLock )
		WHERE )
		Begin
			INSERT INTO users(email) 
			VALUES(@user_email)
			Select  1
		End
	ELSE
		Select  0

   INSERT INTO forms(user_id, book_id, dt_req_take) 
   VALUES(@user_id, 
		  @book_id, 
		   GETDATE())	
   
END
