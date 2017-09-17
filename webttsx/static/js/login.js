/**
 * Created by python on 17-9-16.
 */
$(function(){

	var error_name = false;
	var error_password = false;


	$('#username').blur(function() {
		check_user_name();
	});

	$('#pwd').blur(function() {
		check_pwd();
	});



	function check_user_name(){
		var len = $('#username').val().length;
		if(len<5||len>20)
		{
			$('#username').next().html('请输入5-20个字符的用户名').show();
			error_name = true;
		}
		else
		{
			$('#username').next().hide();
			error_name = false;

		}
	}
	function check_pwd(){
		var len = $('#pwd').val().length;
		if(len<8||len>20)
		{
			$('#pwd').next().html('密码最少8位，最长20位').show();
			error_password = true;
		}
		else
		{
			$('#pwd').next().hide();
			error_password = false;
		}
	}

	$('#login_form').submit(function() {
		check_user_name();
		check_pwd();


		if(error_name == false && error_password == false)
		{
			return true;
		}
		else
		{
			return false;
		}

	});



});