require "erb"
require "highline/import"
require "tmpdir"

task :default => [:bp]



desc 'Creates new blueprint'
task :bp do
  name = ask("Blueprint name? (valid module name):") do
    |q|
    q.validate = /^[a-z][a-z0-9_]*$/
  end
  url_prefix = ask("what is URL prefix? ") do
    |q|
    q.default = "/" + name.sub(/_/, "-") + "/"
    q.validate = /^\/.*$/
  end
  has_static = agree("Has static folder?", true)
  has_templates = agree("Has templates fodler?", true)

  
  base = File.join(Dir.tmpdir, rand.to_s)
  mkdir base
  project = File.join(base, name)
  mkdir project
  template = ERB.new <<EOF
import flask

from flask import blueprints


"""
<%= "="*(name.length + " blueprint".length) %>
<%= name %> blueprint
<%= "="*(name.length + " blueprint".length) %>


"""

BP = blueprints.Blueprint('<%= name %>', __name__,<% if has_static then %>
    static_folder='static', <% end %><% if has_templates then %>
    template_folder='templates',
    <% end %>url_prefix='<%= url_prefix %>')
    
# write your stuff here
EOF
  File.new(File.join(project, "__init__.py"), "w").write(template.result(binding))
  if has_static then
    static = File.join(project, "static")
    %w(css img js).each {|x| mkdir_p File.join(static, x)}
  end
  if has_templates then
    mkdir_p File.join(project, "templates", name, "haml")
  end
  mv project, File.expand_path("focus2/blueprints/")
  rm_r base

end
