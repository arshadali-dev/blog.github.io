# frozen_string_literal: true

require "json"
require "open3"
require "optparse"
require "rbconfig"

Dir.chdir(File.expand_path("../..", __dir__))
destination = "_site"
OptionParser.new do |options|
  options.banner = "Usage: ruby .github/scripts/build_site.rb [--destination DIRECTORY]"
  options.on("--destination DIRECTORY") { |value| destination = value }
end.parse!
abort("Unexpected arguments: #{ARGV.join(' ')}") unless ARGV.empty?

revision = ENV["CF_PAGES_COMMIT_SHA"] || ENV["GITHUB_SHA"]
unless revision
  revision, status = Open3.capture2("git", "rev-parse", "HEAD")
  abort("Cannot determine the source revision") unless status.success?
end
revision = revision.strip
abort("Invalid source revision: #{revision}") unless revision.match?(/\A[0-9a-f]{40}\z/)

success = system(
  RbConfig.ruby, "-S", "bundle", "exec", "jekyll", "build",
  "--strict_front_matter", "--destination", destination
)
unless success
  warn("Jekyll build failed; deployment metadata was not written.")
  exit($?.exitstatus || 1)
end

File.write(
  File.join(destination, "build-info.json"),
  JSON.pretty_generate({ "revision" => revision }) + "\n"
)
puts("Built revision #{revision}")
