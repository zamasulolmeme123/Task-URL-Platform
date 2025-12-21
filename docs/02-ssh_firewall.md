# Настройка подключения по ssh к VPS

Для подключения к VPS мы будем использовать ssh-подключение. 


- Далее настраиваем подключение 

Для этого:
- Создаем ssh-ключ на windows(cmd):

```
    ssh-keygen -t ed25519
```

- Далее либо сразу копируем новый ssh-ключ либо с помощью команды достаем его и копируем, команда(cmd):

```
    type C:\Users\Рома\.ssh\id_ed25519.pub
```

- Далее вставляем новый ssh-ключ на нашем linux-сервере по пути:

```
    nano ~/.ssh/authorized_keys #добавляем строку с нашим ssh-ключом и сохраняем
```

- Настраиваем подключение без паролей, только по ssh:

```
    sudo nano /etc/ssh/sshd_config
```

- Добавляем или изменяем строки:

```
    PubkeyAuthentication yes
    PasswordAuthentication no
    PermitRootLogin no
```

- Перезапускаем сервис ssh:

```
    sudo systemctl restart ssh
```

- Пробуем подключаться через cmd:

```
    ssh name@ip #Должно автоматически подключиться без паролей
```

## Firewall

- Настраиваем ВМ на подключение только с нашего ip :

```
    sudo ufw allow from Наш_ip to any port 22 proto tcp
```


![alt text](./images/image-3.png)

## Nginx

- Настраиваем подключение к nginx тоже только с нашего ip

```
    sudo ufw allow from Наш_ip to any port 8080 proto tcp
```


![alt text](./images/image-4.png)

