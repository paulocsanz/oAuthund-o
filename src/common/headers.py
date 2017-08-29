#    Sets appropriate headers to response, protecting the server's and
#    the client's security. Limits client behavior to the intended by
#    the server, register violations.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import url_for, request

class SecureHeader:
    def __init__(self, app):
        @app.after_request
        def fix_headers(response):
            """
            Overwrite headers to safe versions (blocks a lot of
            things by default, be aware)

            We should allow passing customizations as argument, maybe at
            config
            """

            response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Download-Options'] = 'noopen'
            response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
            response.headers['Content-Security-Policy'] = (
                "default-src 'none';"
                "script-src 'none';"
                "style-src 'self';"
                "img-src 'self';"
                "connect-src 'none';"
                "font-src 'none';"
                "object-src 'none';"
                "media-src 'self';"
                "sandbox allow-forms;"
                "report-uri {};"
                "child-src 'none';"
                "form-action 'self';"
                "frame-ancestors 'none';"
                "plugin-types 'application/pdf';"
                .format(url_for('csp_report')))
            response.headers['Server'] = ''
            response.headers.pop('ETag', None)
            return response

        # If the rules are broken log warning request made by the browser
        @app.route('/csp_report', methods=["POST"])
        def csp_report():
            app.config['log'].json("CSP_REPORT [GET]", dict(request.args))
            app.config['log'].json("CSP_REPORT [POST]", dict(request.form))
            return 'OK', 200

