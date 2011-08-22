require File.expand_path('../environment', __FILE__)
require 'sinatra'
require 'net/http'
require 'uri'
require 'wikitext'

get '/' do
  Article.count.to_s
end

get '/wiki/:name' do
  name     = params[:name].gsub(/^(.)/) { $1.upcase }
  @article = Article.find_by_name(name)
  uri      = URI.parse("#{FILE_HOST}?offset=#{@article.offset}&length=#{@article.length}")
  text     = Net::HTTP.get_response(uri).body

  text.force_encoding('UTF-8') if text.respond_to?(:force_encoding) # ugh
  text.gsub!(/\{\{[^\}]*\}\}/, '')

  @html = Wikitext::Parser.new.parse(text)
  @name = params[:name]
  erb :article
end

post '/wiki/:name/star' do
  #TODO: Mark this article as starred
end
