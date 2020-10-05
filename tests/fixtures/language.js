// Compliant
variable_password0 = password;
variable_password1 = $password;
let variable_password2 = "$password";
var variable_password3 = "${password}";
const variable_password4 = "{{ password }}";
variable_password5 = "{{ THIS_IS_A_VERY_LONG_A_PLACEHOLDER_FOR_PASSWORD }}";
variable_password6 = "{password}";
variable_password7 = "{ password }";
variable_password8 = "obj.aFunctionCall()";

// Noncompliant
static_password01 = "hardcoded0";
let static_password02 = "hardcoded1";
var static_password03 = "hardcoded2";
const static_password04 = "hardcoded3";
