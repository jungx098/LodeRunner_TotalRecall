# Lode Runner - Total Recall is a static site: HTML, JS and assets, no build
# step and no server-side code.  It needs a real HTTP server rather than
# file:// because the browser scopes localStorage (saved progress, custom
# levels, theme choice) per origin.
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html/

EXPOSE 80
