#!/usr/bin/env python3
"""Email sending utility using smtplib with support for HTML and attachments."""

import argparse
import email.message
import email.policy
import json
import mimetypes
import os
import smtplib
import ssl
import sys
from email.utils import formataddr
from pathlib import Path
from typing import Optional


def read_template(template_path: str, variables: dict) -> str:
    """Read email template and substitute variables.

    Template variables should be in format {{variable_name}}.

    Args:
        template_path: Path to template file
        variables: Dictionary of variable substitutions

    Returns:
        Rendered email content
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for key, value in variables.items():
        content = content.replace('{{' + key + '}}', str(value))

    return content


def send_email(
    to: str,
    subject: str,
    content: str,
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    from_addr: Optional[str] = None,
    from_name: Optional[str] = None,
    content_type: str = 'html',
    attachments: Optional[list[str]] = None,
    use_tls: bool = True,
    use_ssl: bool = False,
) -> bool:
    """Send email via SMTP.

    Args:
        to: Recipient email address
        subject: Email subject
        content: Email body content
        smtp_server: SMTP server hostname
        smtp_port: SMTP server port
        username: SMTP username
        password: SMTP password
        from_addr: Sender email address (defaults to username)
        from_name: Sender display name
        content_type: 'html' or 'plain'
        attachments: List of file paths to attach
        use_tls: Use STARTTLS encryption
        use_ssl: Use SSL encryption (exclusive with use_tls)

    Returns:
        True if successful, False otherwise
    """
    if from_addr is None:
        from_addr = username

    msg = email.message.EmailMessage(policy=email.policy.default)

    msg['To'] = to
    msg['Subject'] = subject

    if from_name:
        msg['From'] = formataddr((from_name, from_addr))
    else:
        msg['From'] = from_addr

    if content_type == 'html':
        msg.set_content(content, subtype='html')
    else:
        msg.set_content(content)

    if attachments:
        for filepath in attachments:
            path = Path(filepath)
            if not path.exists():
                print(f"Warning: Attachment not found: {filepath}", file=sys.stderr)
                continue

            mime_type, encoding = mimetypes.guess_type(filepath)
            if mime_type is None:
                mime_type = 'application/octet-stream'

            main_type, sub_type = mime_type.split('/', 1)

            with open(filepath, 'rb') as f:
                msg.add_attachment(
                    f.read(),
                    maintype=main_type,
                    subtype=sub_type,
                    filename=path.name,
                )

    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(username, password)
                server.send_message(msg)
        else:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls(context=context)
                server.login(username, password)
                server.send_message(msg)

        print(f"Email sent successfully to {to}")
        return True

    except Exception as e:
        print(f"Failed to send email: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='Send email via SMTP')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--content', help='Email body content (or use --template)')
    parser.add_argument('--template', help='Path to email template file')
    parser.add_argument('--template-vars', help='JSON string of template variables')
    parser.add_argument('--smtp-server', required=True, help='SMTP server hostname')
    parser.add_argument('--smtp-port', type=int, required=True, help='SMTP server port')
    parser.add_argument('--username', required=True, help='SMTP username')
    parser.add_argument('--password', required=True, help='SMTP password')
    parser.add_argument('--from-addr', help='Sender email address (default: username)')
    parser.add_argument('--from-name', help='Sender display name')
    parser.add_argument('--content-type', choices=['plain', 'html'], default='plain',
                        help='Content type (default: plain)')
    parser.add_argument('--attach', action='append', help='File attachment (can be used multiple times)')
    parser.add_argument('--no-tls', action='store_true', help='Disable STARTTLS')
    parser.add_argument('--use-ssl', action='store_true', help='Use SSL instead of STARTTLS')

    args = parser.parse_args()

    if args.template and args.content:
        print("Error: Cannot specify both --template and --content", file=sys.stderr)
        sys.exit(1)

    if args.template:
        if not args.template_vars:
            print("Warning: No template variables provided", file=sys.stderr)
            variables = {}
        else:
            variables = json.loads(args.template_vars)
        content = read_template(args.template, variables)
    elif args.content:
        content = args.content
    else:
        content = ""

    success = send_email(
        to=args.to,
        subject=args.subject,
        content=content,
        smtp_server=args.smtp_server,
        smtp_port=args.smtp_port,
        username=args.username,
        password=args.password,
        from_addr=args.from_addr,
        from_name=args.from_name,
        content_type=args.content_type,
        attachments=args.attach,
        use_tls=not args.no_tls,
        use_ssl=args.use_ssl,
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
