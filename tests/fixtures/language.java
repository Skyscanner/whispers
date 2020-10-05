public class language {
    static final String COMPLIANT_APITOKEN = "{token}";
    static final String NONCOMPLIANT_APITOKEN = "YXNkZmZmZmZm_HARDcoded";
    public static void main(String[] args) {
        // Compliant
        String variable_password1 = NONCOMPLIANT_APITOKEN;
        final String variable_password2 = "$password";
        String variable_password3 = "${password}";
        String variable_password4 = "{{ password }}";
        String variable_password5 = "{{ THIS_IS_A_VERY_LONG_A_PLACEHOLDER_FOR_PASSWORD }}";
        String variable_password6 = "{password}";
        String variable_password7 = "{ password }";
        String variable_password8 = System.getProperty("password");

        // Noncompliant
        String static_password01 = "hardcoded0";
        final String static_password02 = "hardcoded1";
    }
}
