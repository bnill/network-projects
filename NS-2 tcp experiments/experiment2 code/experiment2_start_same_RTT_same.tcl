lassign $argv TCP1_SOURCE TCP2_SOURCE CBR_RATE
#Create a simulator object
set ns [new Simulator]

#Open the ns trace file
set tf [open $TCP1_SOURCE-$TCP2_SOURCE-$CBR_RATE.tr w]
$ns trace-all $tf

#Define a finish procedure
proc finish {} {
        global ns tf
        $ns flush-trace
        close $tf
        exit 0
}

if { $TCP1_SOURCE != "TCP" } {
	set TCP1_SOURCE TCP/$TCP1_SOURCE
}

if { $TCP2_SOURCE != "TCP" } {
	set TCP2_SOURCE TCP/$TCP2_SOURCE
}

#Create six nodes
set node_(N1) [$ns node]
set node_(N2) [$ns node]
set node_(N3) [$ns node]
set node_(N4) [$ns node]
set node_(N5) [$ns node]
set node_(N6) [$ns node]

#Create duplex links between the nodes
$ns duplex-link $node_(N1) $node_(N2) 10Mb 2ms DropTail
$ns duplex-link $node_(N2) $node_(N3) 10Mb 2ms DropTail
$ns duplex-link $node_(N3) $node_(N4) 10Mb 2ms DropTail
$ns duplex-link $node_(N5) $node_(N2) 10Mb 2ms DropTail
$ns duplex-link $node_(N3) $node_(N6) 10Mb 2ms DropTail

#Set Queue Size
$ns queue-limit $node_(N1) $node_(N2) 50
$ns queue-limit $node_(N2) $node_(N3) 50
$ns queue-limit $node_(N3) $node_(N4) 50

#TCP1 Source at n1 and TCP Sink at n4
#change tcp types here
set tcp1 [new Agent/$TCP1_SOURCE] 
$tcp1 set class_ 0
$tcp1 set window_ 5000
$ns attach-agent $node_(N1) $tcp1
set sink [new Agent/TCPSink]
$ns attach-agent $node_(N4) $sink
$ns connect $tcp1 $sink

#Setup a FTP Agent over the TCP connection or TCP won't be implemented
#according to the document
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP

#TCP2 Source at n5 and TCP Sink at n6
#change tcp types here
set tcp2 [new Agent/$TCP2_SOURCE] 
$tcp2 set class_ 1
$tcp2 set window_ 5000
$ns attach-agent $node_(N5) $tcp2
set sink [new Agent/TCPSink]
$ns attach-agent $node_(N6) $sink
$ns connect $tcp2 $sink

#Setup a FTP Agent over the TCP connection or TCP won't be implemented
#according to the document
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP

#udp used for cbr
set udp [new Agent/UDP]
$ns attach-agent $node_(N2) $udp
set null [new Agent/Null]
$ns attach-agent $node_(N3) $null
$ns connect $udp $null

#Setup a CBR over UDP connection
#Change CBR rate here
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ $CBR_RATE
$cbr set random_ false

#Schedule events for the CBR and TCP
$ns at 5.0 "$ftp1 start"
$ns at 40.0 "$ftp1 stop"
$ns at 5.0 "$ftp2 start"
$ns at 40.0 "$ftp2 stop"
$ns at 5.0 "$cbr start"
$ns at 40.0 "$cbr stop"

#Call the finish procedure 
$ns at 50.0 "finish"

#Run the simulation
$ns run
