<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Warp Skeleton Site</title>

    <link rel="icon" type="image/vnd.microsoft.icon" href="/favicon.ico"></link>

<%include file="/standard/includes.mak" />
<%include file="/jqgrid/includes.mak" />

    <link rel="stylesheet" href="/css/site.css" type="text/css"></link>
    <link rel="stylesheet" href="/_warp/warp.css" type="text/css"></link>

  </head>

  <body>

   <div class="header">
     <h1>Warp Skeleton Site</h1>

     <div class="nav-bar">
       <span class="links">
         <a href="/">Home</a>
       </span>

       <span class="login">
% if request.avatar:
  <form method="POST" action="/__logout__">
    Logged in as <strong>${request.avatar.email}</strong>
    <input type="submit" value = "Log Out" />
  </form>
% else:
<form method="POST" action="/__login__">
  <input type="text" name="email" value="Username" class="warp-autoclear" />
  <input type="password" name="password" value="Password" class="warp-autoclear" />
  <input type="submit" value="Log in" />
</form>
% endif
      </span>

      <div style="clear:both"></div>

    </div>

  </div>

  <div class="content">
    ${self.body()}
  </div>

  </body>
</html>
