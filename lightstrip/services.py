import random
import socket
import string
import time


class LightStripProvider:
    def __init__(self, device):
        self.device = device

    def dispatch(self, payload):
        if isinstance(payload, list):
            return self.dispatch_batch(payload)
        return self._dispatch_socket_commands([payload], batch_mode=False)

    def dispatch_batch(self, payloads):
        return self._dispatch_socket_commands(payloads, batch_mode=True)

    def _dispatch_socket_commands(self, payloads, batch_mode):
        endpoint = (self.device.endpoint or '').strip()
        if not endpoint:
            return {
                'status': 'simulated',
                'message': 'No endpoint configured, simulated provider accepted the command.',
                'payload': payloads,
                'transport': 'tcp_socket'
            }

        host = ''
        port = None
        responses = []
        sock = None
        try:
            host, port = self._parse_endpoint(endpoint)
            command_items = [self._build_command_item(payload) for payload in payloads]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self._socket_timeout())
            sock.connect((host, port))
            for item in command_items:
                wire_data = item['command'] + '\r\n'
                sock.sendall(wire_data.encode('utf-8'))

            response_map = self._read_batch_command_responses(sock, command_items)
            for item in command_items:
                item_responses = response_map.get(item['trace'], [])
                responses.append({
                    'trace': item['trace'],
                    'command': item['command'],
                    'payload': item['payload'],
                    'responses': item_responses,
                    'status': self._derive_item_status(item_responses)
                })
            return {
                'status': self._derive_status(responses),
                'message': 'Batch command accepted by socket provider.' if batch_mode else 'Command accepted by socket provider.',
                'transport': 'tcp_socket',
                'host': host,
                'port': port,
                'payload': payloads,
                'command_results': responses
            }
        except Exception as exc:
            return {
                'status': 'failed',
                'message': str(exc),
                'transport': 'tcp_socket',
                'host': host,
                'port': port,
                'payload': payloads,
                'command_results': responses
            }
        finally:
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass

    def _build_command_item(self, payload):
        product_type = str(self.device.extra_config.get('product_type', 'ptl')).lower()
        trace = self._build_trace()
        command_type = str(payload.get('command') or 'on').lower()
        if command_type == 'set_sku':
            command = self._build_ptl_set_sku_command(payload, trace)
        elif product_type == 'tag':
            command = self._build_tag_control_command(payload, trace)
        else:
            command = self._build_ptl_ctrl_command(payload, trace)
        return {
            'trace': trace,
            'command': command,
            'payload': payload,
            'expect_async': True
        }

    def _build_tag_control_command(self, payload, trace):
        extra_payload = payload.get('extra_payload') or {}
        color = self._normalize_color(payload.get('color') or extra_payload.get('color') or 'green')
        if payload.get('command') == 'off':
            color = 'off'
        beep = int(extra_payload.get('beep', 0))
        ontime = int(extra_payload.get('ontime', self.device.extra_config.get('ontime', 2)))
        return 'cmd=tag_control,dn={dn},led={color},beep={beep},ontime={ontime},trace={trace}'.format(
            dn=payload['light_address'],
            color=color,
            beep=beep,
            ontime=ontime,
            trace=trace
        )

    def _build_ptl_ctrl_command(self, payload, trace):
        extra_payload = payload.get('extra_payload') or {}
        command = payload.get('command', 'on')
        left_color = self._normalize_color(extra_payload.get('left_color') or payload.get('color') or 'green')
        right_color = self._normalize_color(extra_payload.get('right_color') or payload.get('color') or 'green')
        if command == 'off':
            left_color = 'off'
            right_color = 'off'
        led_brightness = int(extra_payload.get('led_brightness', self.device.extra_config.get('led_brightness', 2)))
        beep_mode = int(extra_payload.get('beep_mode', 0))
        beep_vol = int(extra_payload.get('beep_vol', self.device.extra_config.get('beep_vol', 1)))
        lcd_brightness = int(extra_payload.get('lcd_brightness', self.device.extra_config.get('lcd_brightness', 2)))
        lcd_num_val = int(extra_payload.get('lcd_num_val', 0))
        ontime = int(extra_payload.get('ontime', self.device.extra_config.get('ontime', 2)))
        parts = [
            'cmd=ptl_ctrl',
            'dn={}'.format(payload['light_address']),
            'led_brightness={}'.format(led_brightness),
            'led_group1_color={}'.format(left_color),
            'led_group2_color={}'.format(right_color),
            'beep_mode={}'.format(beep_mode),
            'beep_vol={}'.format(beep_vol),
            'lcd_brightness={}'.format(lcd_brightness),
            'lcd_num_val={}'.format(lcd_num_val),
            'ontime={}'.format(ontime),
            'trace={}'.format(trace),
        ]
        led_flash = extra_payload.get('led_flash')
        if led_flash is not None:
            parts.insert(2, 'led_flash={}'.format(int(led_flash)))
        return ','.join(parts)

    def _build_ptl_set_sku_command(self, payload, trace):
        extra_payload = payload.get('extra_payload') or {}
        sku = str(extra_payload.get('sku', '')).strip().upper()
        if not sku:
            raise ValueError('PTL SKU command requires sku')
        return 'cmd=ptl_set_sku,dn={dn},sku={sku},trace={trace}'.format(
            dn=payload['light_address'],
            sku=sku[:6],
            trace=trace
        )

    def _read_batch_command_responses(self, sock, command_items):
        traces = {item['trace'] for item in command_items}
        responses = {trace: [] for trace in traces}
        completed = set()
        buffered = ''
        deadline = time.monotonic() + self._socket_timeout()
        while traces - completed and time.monotonic() < deadline:
            try:
                remaining = deadline - time.monotonic()
                sock.settimeout(max(0.1, remaining))
                chunk = sock.recv(10240)
            except socket.timeout:
                break
            if not chunk:
                break
            buffered += chunk.decode('utf-8', errors='ignore')
            lines = buffered.split('\n')
            buffered = lines.pop() if lines else ''
            for raw_line in lines:
                line = raw_line.strip()
                if not line:
                    continue
                trace = self._extract_response_trace(line)
                if trace not in traces:
                    continue
                responses[trace].append(line)
                if self._is_terminal_response(line):
                    completed.add(trace)
        return responses

    def _derive_status(self, command_results):
        if not command_results:
            return 'failed'
        statuses = [item.get('status') or self._derive_item_status(item.get('responses') or []) for item in command_results]
        if any(status == 'failed' for status in statuses):
            return 'failed'
        if all(status == 'success' for status in statuses):
            return 'success'
        if any(status == 'accepted' for status in statuses):
            return 'accepted'
        return 'failed'

    def _derive_item_status(self, lines):
        if not lines:
            return 'failed'
        normalized_lines = [line.upper() for line in lines]
        result_lines = [line for line in normalized_lines if 'RESULT=' in line or 'RT=' in line]
        if result_lines:
            return 'success' if any('RESULT=OK' in line for line in result_lines) else 'failed'
        if any('CMD=ACCEPT' in line for line in normalized_lines):
            return 'accepted'
        return 'failed'

    def _is_terminal_response(self, line):
        upper_line = line.upper()
        return 'RT=' in upper_line or 'RESULT=' in upper_line

    def _extract_response_trace(self, line):
        upper_line = line.upper()
        marker = 'TRACE='
        index = upper_line.find(marker)
        if index < 0:
            return None
        trace = line[index + len(marker):].strip()
        for separator in [',', ' ', '\r', '\n']:
            if separator in trace:
                trace = trace.split(separator, 1)[0]
        return trace.strip()

    def _parse_endpoint(self, endpoint):
        if ':' in endpoint:
            host, port = endpoint.rsplit(':', 1)
            return host.strip(), int(port.strip())
        return endpoint, int(self.device.extra_config.get('port', 5000))

    def _socket_timeout(self):
        return int(self.device.extra_config.get('socket_timeout', 8))

    def _build_trace(self):
        alphabet = string.ascii_uppercase + string.digits
        length = int(self.device.extra_config.get('trace_length', 8))
        length = 16 if length > 16 else length
        length = 4 if length < 4 else length
        return ''.join(random.choice(alphabet) for _ in range(length))

    def _normalize_color(self, color):
        value = str(color or 'green').strip().lower()
        if value == 'orange':
            return 'yellow'
        allowed = {'off', 'red', 'purple', 'yellow', 'green', 'blue', 'cyan', 'white'}
        return value if value in allowed else 'green'
