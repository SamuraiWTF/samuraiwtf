# Change next line to reflect your env Java 1.6
JAVA_HOME="/your/java/home_path"
#different classpath per OS
PARSERCLASSPATH="wsdlparser/wsdlparser.jar:wsdlparser/bcprov-jdk15-144.jar:wsdlparser/commons-beanutils-1.7.0.jar:wsdlparser/commons-cli-1.0.jar:wsdlparser/commons-codec-1.3.jar:wsdlparser/commons-httpclient-3.1.jar:wsdlparser/commons-logging-1.1.1.jar:wsdlparser/javaee.jar:wsdlparser/log4j-1.2.14.jar:wsdlparser/not-yet-commons-ssl-0.3.11.jar:wsdlparser/soapui-3.5.1.jar:wsdlparser/soapui-xmlbeans-3.5.1.jar:wsdlparser/temp.tx:wsdlparser/wsdl4j-1.6.2-fixed.jar:wsdlparser/xbean-fixed-2.4.0.jar:wsdlparser/xbean_xpath-2.4.0.jar:wsdlparser/xercesImpl-2.9.1.jar"

$JAVA_HOME/bin/java -cp $PARSERCLASSPATH -Djava.awt.headless=true com.sop.services.wsdl.ParseWsdl $1 $2
