<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Warp Skeleton</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <link rel="icon" type="image/vnd.microsoft.icon" href="/favicon.ico">
    <link rel="stylesheet" href="/_warp/css/bootstrap.min.css">
    <link rel="stylesheet" href="/css/site.css">
    
    <%include file="/standard/bootstrap.mak" />
  </head>

  <body>
    
    <header>
      <div class="navbar navbar-inverse">
        <div class="navbar-inner">
          <div class="container">
            <a class="brand" href="/">Warp speed!</a>
            % if request.avatar:
            <form class="navbar-form pull-right" method="POST" action="/__logout__">
              <button type="submit" class="btn btn-primary">Log Out</button>
            </form>
            <span class="navbar-text pull-right">Logged in as <strong>${request.avatar.email}</strong>&nbsp;&nbsp;</span>
            % else:
            <form class="navbar-form pull-right" method="POST" action="/__login__">
              <input type="text" name="email" placeholder="Email">
              <input type="password" name="password" placeholder="Password">
              <button type="submit" class="btn btn-primary">Log In</button>
            </form>
            % endif
          </div>
        </div>
      </div>
    </header>
      
    <div class="container-fluid">
      <div class="row-fluid">
        
        <div class="span2">
          <%! from warp.helpers import link, getNode %>
          <%! from warp.common import access %>
    
          <%def name="navEntry(label, linkNode, linkFacet)">
          <%
          attrs = {}
          if not access.allowed(request.avatar, linkNode):
             return ""
          active = ""
          if request.prepath[0] == linkNode.__name__.split('.')[1]:
              active = "active"
          theLink = link("<i class=\"icon-chevron-right\"></i>" + label, linkNode, linkFacet)
          %>
          <li class="${active}">${theLink}</li>
          </%def>
    
          <ul class="nav nav-list site-mainnav">
          <%
          for (label, nodeName, linkFacet) in (
             ("Home", "home", "index"),
             ("Widgets", "widgets", "index"),
          ):
            navEntry(label, getNode(nodeName), linkFacet)
          %>
          </ul>
        </div>
          
        <div class="span10">        
          % for message, args, kwargs in request.session.getFlashMessages(): 
          <div class="warp-message">
            ${t(message, *args, **kwargs)}
          </div>
          % endfor
  
          <%def name="breadCrumbs()"><% return [] %></%def>
          <% crumbs = self.breadCrumbs() %>
          % if crumbs:
            <ul class="breadcrumb">
            % for i, crumb in enumerate(crumbs):
              <% linker = getattr(crumb, 'linkAsParent', None) %>
              <% if linker is None: continue %>
              % if i:
                <span class="divider">&raquo;</span>
              % endif
              <li>${linker(request)}</li>
            % endfor
            </ul>
          % endif
  
          <div class="page-header">
          <%def name="contentHeader()">
              <h1>Content header goes here</h1>
          </%def>
          <%self:contentHeader>
          </%self:contentHeader>
          </div>
          
          <div id="content">
          ${self.body()}
          </div>
        </div>
      
      </div>
    </div>
    
    <footer>
      <div class="container-fluid">
        <p>Footer information goes here</p>
      </div>
    </footer>

  </body>
</html>
