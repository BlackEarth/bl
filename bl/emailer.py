# bl.emailer - a mailer class

import sys, smtplib, traceback
from email.mime.text import MIMEText
from bl.dict import Dict

class Emailer(Dict):
    """create and send email using templates. Parameters (*=required):
        template*   : must have a render() or generate() method that takes keyword arguments
        server      : The address of the mail server
        port        : The port the server is listening on
        from_address: The default From address
        to_address  : The default To address
        delivery    : 'smtp' sends it, 'test' returns the rendered message 
        username    : username for smtp auth
        password    : password for smtp auth
        debug       : Whether debugging is on
    """

    def __init__(self, template, server='127.0.0.1', port='25', delivery='test', debug='True', **params):
        "set up an emailer with a particular config and template"
        Dict.__init__(self, **params)
        self.template = template
        self.DEBUG = self.get('debug') and self.pop('debug') or None

    def __repr__(self):
        return "Emailer(%r)" % (self.template)

    def send_message(self, to_addr=None, subject=None, from_addr=None, cc=None, bcc=None, **context):
        return self.send(
            self.message(
                to_addr=to_addr, from_addr=from_addr, cc=cc, bcc=bcc, 
                subject=subject, 
                **context))

    def render(self, **context):
        """render the emailer template with the given context."""
        render_method = self.template.__dict__.get('render') or self.template.__dict__.get('generate')
        r = render_method(c=Dict(**context))
        if type(r)=='bytes': r = r.decode('UTF-8')

    def message(self, to_addr=None, subject=None, from_addr=None, cc=None, bcc=None, **context):
        "create a MIMEText message from the msg text with the given msg args"
        msg = MIMEText(self.render(to_addr=to_addr or self.to_address, from_addr=from_addr, cc=cc, bcc=bcc, **context))
        msg['From'] = from_addr or self.from_address
        msg['Subject'] = subject
        for addr in (to_addr or self.to_address or '').split(','):
            msg.add_header('To', addr.strip())
        for addr in (cc or '').split(','):
            msg.add_header('Cc', addr.strip())
        for addr in (bcc or '').split(','):
            msg.add_header('Bcc', addr.strip())
        return msg

    def send(self, msg):
        """send the given msg and return the status of the delivery.
        Returns None if delivery succeeded.
        Returns a sys.exc_info() tuple if the SMPT client raised an exception.
        """
        if self.delivery == 'test':
            # return the message as text that would be sent
            return msg.as_string()

        elif self.delivery == 'smtp':
            # parse the message and send it
            fromaddr = msg['From']
            tolist = (msg.get_all('To') or []) \
                    + (msg.get_all('Cc') or []) \
                    + (msg.get_all('Bcc') or [])
            try:
                if self.port is not None:
                    smtpclient = smtplib.SMTP(self.server or '127.0.0.1', self.port)
                else:
                    smtpclient = smtplib.SMTP(self.server or '127.0.0.1')
                smtpclient.set_debuglevel(self.DEBUG and 1 or 0)    # non-zero gives us exceptions when emailing.
                if self.username is not None and self.password is not None:
                    smtpclient.login(self.username, self.password)
                for toaddr in tolist:
                    smtpclient.sendmail(fromaddr, toaddr, msg.as_string())
                smtpclient.quit()
            except:
                if self.DEBUG==True: 
                    traceback.print_exc()
                else:
                    print("Emailer exception:", sys.exc_info()[1], file=sys.stderr)
                return sys.exc_info()[1]        # return the exception rather than raising it -- the show must go on.        
