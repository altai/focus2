watch(/.+\.haml/) do 
  |m|
  out = m[0].sub(/haml\//, '').sub(/haml$/, 'html')
  system("haml --format html5 #{ m[0] } #{ out }")
end
