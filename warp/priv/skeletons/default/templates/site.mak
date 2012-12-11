<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Warp Skeleton</title>

    <link rel="icon" type="image/vnd.microsoft.icon" href="/favicon.ico"></link>

<%include file="/standard/includes.mak" />
<%include file="/jqgrid/includes.mak" />

    <link rel="stylesheet" href="/css/site.css" type="text/css"></link>
    <link rel="stylesheet" href="/_warp/warp.css" type="text/css"></link>

  </head>

  <body>

   <div class="header">

     <div class="topbar">
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

      <div style="clear: both"></div>

     </div>

     <div class="logo">
       <h1><a href="/">Warp Site</a></h1>
       <h2>Subtitle Goes Here</h2>
       <hr />
     </div>

     <div class="nav-bar">

<%! from warp.helpers import link, getNode %>
<%! from warp.common import access %>

<%def name="navEntry(label, linkNode, linkFacet)">
<%
attrs = {}
if not access.allowed(request.avatar, linkNode):
   return ""
if request.prepath[0] == linkNode.__name__.split('.')[1]:
   attrs["class"] = "active"
theLink = link(label, linkNode, linkFacet, **attrs)
%>
${theLink}
</%def>

<%
for (label, nodeName, linkFacet) in (
   ("Home", "home", "index"),
):
      navEntry(label, getNode(nodeName), linkFacet)
%>

      <div style="clear: both"></div>

    </div>

    <div class="subnav">
      <%def name="subnav()">
        Sub-navigation links will go here.
      </%def>
      <%self:subnav>
      </%self:subnav>
    </div>

  </div>

  <div class="content-wrapper">  
    <%def name="breadCrumbs()"><% return [] %></%def>
    <% crumbs = self.breadCrumbs() %>
    % if crumbs:
      <div class="warp-breadcrumbs">
      % for i, crumb in enumerate(crumbs):
        <% linker = getattr(crumb, 'linkAsParent', None) %>
        <% if linker is None: continue %>
        % if i:
          &gt;
        % endif
        ${linker(request)}
      % endfor
      </div>
    % endif

    % for message, args, kwargs in request.session.getFlashMessages(): 
      <div class="warp-message">
        ${t(message, *args, **kwargs)}
      </div>
    % endfor

    <div class="content">

      <div class="content-header">
        <%def name="contentHeader()">
          Content header goes here.
        </%def>
        <%self:contentHeader>
        </%self:contentHeader>
      </div>

      <div class="inner">
        ${self.body()}
      </div>
      <div style="clear: both"></div>
    </div>
  </div>

  <div class="footer">
   Footer information goes here.
  </div>

  </body>
</html>
