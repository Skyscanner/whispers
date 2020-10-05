<?php
# Compliant
$variable_password1 = $password;
$variable_password2 = "$password";
$variable_password3 = "${password}";
$variable_password4 = "{{ password }}";
$variable_password5 = "{{ THIS_IS_A_VERY_LONG_A_PLACEHOLDER_FOR_PASSWORD }}";
$variable_password6 = "{password}";
$variable_password7 = "{ password }";
$variable_password8 = aFunctionCall();
$config['db_password'] = '';
define("unset_password", "", true);
define("variable_password", "{placeholder}");

# Noncompliant
$static_password01 = "hardcoded0";
define("static_password02", "hardcoded1", true);
define("static_password03", "hardcoded2");
$config['db_password'] = 'hardcoded3';
?>
