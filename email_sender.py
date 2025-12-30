import smtplib

class SENDMAIL:
    """
    Uses smtplib to send messages from a google server.

    Attributes:
        sender(str): The senders email.
        reciever_email: The recievers email.
        gmail_app_password: The app password recieved from gmail account. Not the account password.
        subject: The subject of the email.
        body: The text body of the email.
    """

    def send_email(self,sender,reciever_email,gmail_app_password,subject,body):
        msg = f'Subject: {subject}\n\n{body}'
        # print(sender,reciever_email,gmail_app_password,subject,body).

        with smtplib.SMTP_SSL(host='smtp.gmail.com',port=465) as server:
            server.login(user=sender,password=gmail_app_password,initial_response_ok=True)
            server.sendmail(from_addr=sender,to_addrs=reciever_email,msg=msg)
            print('Message sent')
