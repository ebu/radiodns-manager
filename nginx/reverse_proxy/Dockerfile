FROM nginx:1.15

COPY nginx.conf /etc/nginx/nginx.conf
ADD static /var/www/media/static

CMD ["nginx", "-g", "daemon off;"]
