#numactl --physcpubind=0-15 java -DenableDebugMethodProfiler=true -jar spigot-1.12.2.jar nogui

# java -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.port=25585 -Dcom.sun.management.jmxremote.ssl=false -Xms8G -Xmx8G -jar server.jar nogui

java -Xms8G -Xmx8G -jar server.jar nogui
