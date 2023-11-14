import re
import flask as f
import paramiko
import psycopg2

app = f.Flask(__name__)

connection_params = {
    'dbname': 'your_database',
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}


def get_info_from_device(ip, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, username, password)
    info = []

    output = ssh.exec_command("lsb_release -a")[1].read().decode('utf-8')
    match = re.compile(r'Distributor ID:\s(.*)$', re.MULTILINE).search(output)
    info.append(match.group(1))
    match = re.compile(r'Release:\s(.*)$', re.MULTILINE).search(output)
    info.append(match.group(1))

    info.append(ssh.exec_command("hostname")[1].read().decode('utf-8').strip())

    cpuinfo_output = ssh.exec_command("cat /proc/cpuinfo")[1].read().decode('utf-8')
    processor_count = re.compile(r'processor\s:(.*)$', re.MULTILINE)
    processor_model = re.compile(r'model name\s:(.*)$', re.MULTILINE)
    info.append(processor_model.search(cpuinfo_output).group(1).strip())
    info.append(len(processor_count.findall(cpuinfo_output)))

    info.append(ssh.exec_command("uname -i")[1].read().decode('utf-8').strip())

    output = ssh.exec_command("cat /proc/meminfo")[1].read().decode('utf-8')
    match = re.compile(r'MemTotal:\s(.*)$', re.MULTILINE).search(output)
    info.append(match.group(1))
    return info


def get_info_from_table():
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM int2;")
    devices = cursor.fetchall()
    print(devices)
    cursor.close()
    conn.close()

    return devices


@app.route('/connect', methods=['POST'])
def execute_command():
    ip = f.request.form['ip']
    port = int(f.request.form['port'])
    username = f.request.form['login']
    password = f.request.form['password']

    info = get_info_from_device(ip, port, username, password)

    return f.render_template('result.html', info=info, ip=ip)


@app.route('/')
def main():
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS int2 (
        ID SERIAL PRIMARY KEY,
        "IP-адрес" VARCHAR(255),
        Дистрибутив VARCHAR(255),
        Версия_дистрибутива VARCHAR(255),
        Имя_системы VARCHAR(255),
        Модель_процессора VARCHAR(255),
        Количество_ядер INTEGER,
        Архитектура_системы VARCHAR(255),
        Количество_оперативной_памяти VARCHAR(255)
    );
""")
    conn.commit()
    cursor.close()
    conn.close()
    return f.render_template('main.html')


@app.route('/database')
def database():
    devices = get_info_from_table()
    return f.render_template('database.html', devices=devices)


@app.route('/connection')
def connection():
    return f.render_template('connection.html')


@app.route('/save_result', methods=['POST'])
def result():
    info = f.request.form.getlist("info[]")
    insert_data_query = """
        INSERT INTO int2 (
            "IP-адрес",
            Дистрибутив,
            Версия_дистрибутива,
            Имя_системы,
            Модель_процессора,
            Количество_ядер,
            Архитектура_системы,
            Количество_оперативной_памяти
        ) VALUES (
            %s , %s, %s, %s, %s, %s, %s, %s
        );
    """
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()
    cursor.execute(insert_data_query, info)
    conn.commit()
    cursor.close()
    conn.close()
    devices = get_info_from_table()
    return f.render_template('database.html', devices=devices)


if __name__ == '__main__':
    app.run(debug=True)
