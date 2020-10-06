package main

func main() {
	// Compliant
	var variable_password1, variable_password2 string = password, "$password"
	const variable_password3 string = "${password}"
	variable_password4 := "{{ password }}"
	var variable_password5 = "{{ THIS_IS_A_VERY_LONG_A_PLACEHOLDER_FOR_PASSWORD }}"
	var variable_password6 = "{password}"
	var variable_password7 = "{ password }"
	var variable_password8 = aFunctionCall()
	msg := "Here is a long, compliant string of text"
	var1, var2 := justOneFunction()

	// Noncompliant
	const static_password01, static_password02 string = "hardcoded0", "hardcoded1"
	var static_password03, dynamic_password01 string = "hardcoded2", "{password}"
	static_password04, static_password05 := "hardcoded3", "hardcoded4"
	static_password06, dynamic_password02 := "hardcoded5", "{password}"
	var static_password07 = "hardcoded6"
	const static_password08 = "hardcoded7"
	static_password09 := "hardcoded8"
}
