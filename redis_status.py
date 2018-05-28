# -*- coding: utf-8 -*-

import sqlite3
import os
import socket

DB = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
CONF = '/etc/collectd.d/redis-info.conf'
PORT = 6379
PASSWORD = '@sentinel'

def write_redis_config(hosts):
    module = '''  <Module redis_info>
    Host "{}"
    Port {}
    Auth "{}"
    Cluster false
    Verbose false

    Redis_connected_clients "gauge"
    Redis_blocked_clients "gauge"
    Redis_rejected_connections "counter"

    Redis_expired_keys "counter"
    Redis_evicted_keys "counter"

    Redis_used_cpu_sys "counter"
    Redis_used_cpu_user "counter"
    
    Redis_used_memory "bytes"
    Redis_used_memory_rss "bytes"
    Redis_mem_fragmentation_ratio "gauge"

    Redis_instantaneous_ops_per_sec "gauge"

    Redis_total_connections_received "counter"
    Redis_total_commands_processed "counter"
    Redis_total_net_input_bytes "counter"
    Redis_total_net_output_bytes "counter"

    Redis_keyspace_hits "derive"
    Redis_keyspace_misses "derive"

    Redis_cmdstat_get_calls "counter"
    Redis_cmdstat_get_usec "counter"
    Redis_cmdstat_get_usec_per_call "gauge"
    
    Redis_cmdstat_set_calls "counter"
    Redis_cmdstat_set_usec "counter"
    Redis_cmdstat_set_usec_per_call "gauge"
    
    Redis_cmdstat_scan_calls "counter"
    Redis_cmdstat_scan_usec "counter"
    Redis_cmdstat_scan_usec_per_call "gauge"

    Redis_db0_keys "gauge"
    Redis_db0_expires "gauge"
    Redis_db0_avg_ttl "gauge"
  </Module>'''

    content = '''<LoadPlugin python>
  Globals true
</LoadPlugin>

<Plugin python>
  ModulePath "/opt/redis-collectd-plugin"
  Import "redis_info"'

  {}
</Plugin>'''

    modules = [ module.format(host, PORT, PASSWORD) for host in hosts ]
    with open(CONF, 'w') as f:
        f.write(content.format('\n'.join(modules)))
	f.write('\n')

def reload_redis_service():
    pass

def get_redis_status():
    # 读数据库
    ok = [] 
    error = []

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        result = c.execute('select ip, port from host')
        # 判断redis连接正常
        for r in result.fetchall():
	    host = str(r[0])
	    port = int(r[1])
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, port))
		ok.append(host)
            except Exception as e:
		error.append(host)
		raise e
            s.close()
    return ok, error

if __name__ == '__main__':
    ok, error = get_redis_status()
    write_redis_config(ok)
