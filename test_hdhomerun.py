        
from hdhomerun import *

def ip2str(ip):
    return '%d.%d.%d.%d' % (ip >> 24, (ip >> 16) & 0xff, (ip >> 8) & 0xff, ip & 0xff)

def id2str(id):
    return '%08X' % id

def show_device_info(dev):
    print "  Id:         ", id2str(dev.get_device_id()), "(", id2str(dev.get_device_id_requested()), ")"
    print "  Address:    ", ip2str(dev.get_device_ip()), "(", ip2str(dev.get_device_ip_requested()), ")"
    print "  Local IP:   ", ip2str(dev.get_local_machine_addr())
    print "  Model:      ", dev.get_model_str()
    print "  Version:    ", dev.get_version()
    print "  Festures:   ", dev.get_supported(None)
    #print "  IR Target:  ", dev.get_ir_target()
    print "  Lineup Loc: ", dev.get_lineup_location()
    print ""

def show_tuner_info(dev):
    print "    Tuner:      ", dev.get_tuner()
    print "    Name:       ", dev.get_name()
    print "    StreamInfo: ", dev.get_tuner_streaminfo()
    print "    Channel:    ", dev.get_tuner_channel()
    print "    ChannelMap: ", dev.get_tuner_channelmap()
    print "    Filter:     ", dev.get_tuner_filter()
    print "    Program:    ", dev.get_tuner_program()
    print "    Target:     ", dev.get_tuner_target()
    print "    Lock Owner: ", dev.get_tuner_lockkey_owner()
    (res, s1, s2) = dev.get_tuner_status()
    print "    Status:     ", s1
    print "      Channel:          ", s2.channel
    print "      Lock Str:         ", s2.lock_str
    print "      Signal Present:   ", s2.signal_present
    print "      Lock Supported:   ", s2.lock_supported
    print "      Lock Unsupported: ", s2.lock_unsupported
    print "      Signal Strength:  ", s2.signal_strength
    print "      Signal Quality:   ", s2.signal_to_noise_quality
    print "      Symbol Quality:   ", s2.symbol_error_quality
    print "      Bits / sec:       ", s2.raw_bits_per_second
    print "      Packets / sec:    ", s2.packets_per_second
    print ""

def scan_callback(dev, detres, scan):
    print scan.frequency, scan.channel_str, scan.status.signal_present,
    if detres != None:
        print dev.channelscan_get_progress()
        for i in range(detres.program_count):
            p = detres.programs[i]
            print "   ", p.program_str, p.type
    else:
        print "No signal"
    return True
    
if True:
    print "Devices found:"
    disc = HdhrDiscovery()
    for dd in disc.devices():
        dev = dd.connect()
        if not not dev:
            show_device_info(dev)
            for j in range(dd.tuner_count):
                dev.set_tuner(j)
                show_tuner_info(dev)
            del dev
        else:
            print "Could not create device", dd.device_id
    print ""
    
if True:
    print "Scanning..."
    dev = HdhrDevice()
    res = dev.scan(scan_callback)
    print str(res)
