### Reverse Proxy & Rewrite response
**Gotchas:**
  - The URI passed to upstream server is determined based on whether **"[proxy_pass]"** directive is used with URI or not. </br>
  Trailing slash in proxy_pass directive means that URI is present and equal to / (source). </br>
  Absense of trailing slash means that URI is absent.
```nginx
        location /some_dir/ { proxy_pass http://some_server/; }
```
```
    # With the above, there's the following proxy:
        http:// your_server/some_dir/ some_subdir/some_file ->
        http:// some_server/          some_subdir/some_file
```
```nginx
        location /some_dir/ { proxy_pass http://some_server; }
```
```
    # With the second (no trailing slash): the proxy goes like this:
        http:// your_server /some_dir/some_subdir/some_file ->
        http:// some_server /some_dir/some_subdir/some_file
```
  - Automatic (PATH) rewrite only works if you don't use variables in proxy_pass. If you use variables, you should do rewrite yourself:
```nginx
        location /some_dir/ {
          rewrite    /some_dir/(.*) /$1 break;
          proxy_pass $upstream_server;
        }
```
  - For response (TEXT) rewrite, you can use the **"[sub_filter]"** directive. Something like ...
```nginx
        location /some_dir/ {
            proxy_pass http://localhost:8080/;
            sub_filter "http://your_server/" "http://your_server/some_dir/";
            sub_filter_once off;
        }
```

### Jenkins Hijinks
[Behind NGINX]
```nginx
upstream jenkins {
  server 127.0.0.1:8080 fail_timeout=0;
}
 
server {
  listen 80;
  server_name jenkins.domain.tld;
  return 301 https://$host$request_uri;
}
 
server {
  listen 443 ssl;
  server_name jenkins.domain.tld;
 
  ssl_certificate /etc/nginx/ssl/server.crt;
  ssl_certificate_key /etc/nginx/ssl/server.key;
 
  location / {
    proxy_set_header        Host $host:$server_port;
    proxy_set_header        X-Real-IP $remote_addr;
    proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header        X-Forwarded-Proto $scheme;
    proxy_redirect http:// https://;
    proxy_pass              http://jenkins;
    # Required for new HTTP-based CLI
    proxy_http_version 1.1;
    proxy_request_buffering off;
    proxy_buffering off; # Required for HTTP-based CLI to work over SSL
    # workaround for https://issues.jenkins-ci.org/browse/JENKINS-45651
    add_header 'X-SSH-Endpoint' 'jenkins.domain.tld:50022' always;
  }
}
```

[proxy_pass]: http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass
[sub_filter]: http://nginx.org/en/docs/http/ngx_http_sub_module.html
[Behind NGINX]: https://wiki.jenkins.io/display/JENKINS/Jenkins+behind+an+NGinX+reverse+proxy
