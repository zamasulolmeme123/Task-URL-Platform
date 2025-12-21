## Подключаем Graphana и Prometheus:


![alt text](./images/image-9.png)



Закрываем порты для безопасности:

```
    sudo ufw deny 3000/tcp
    sudo ufw deny 9090/tcp
    sudo ufw deny 8081/tcp
    sudo ufw status
```


- Подключаемся к graphana по адрессу ip:9090 (admin admin login and password)

- Добавляем prometheus в graphana:


![alt text](./images/image-10.png)


- Добавляем Dashboard:


![alt text](./images/image-11.png)
