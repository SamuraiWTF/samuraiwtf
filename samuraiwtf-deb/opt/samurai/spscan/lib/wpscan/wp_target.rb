# encoding: UTF-8

require 'web_site'
require 'wp_target/malwares'
require 'wp_target/wp_readme'
require 'wp_target/wp_registrable'
require 'wp_target/wp_config_backup'
require 'wp_target/wp_login_protection'
require 'wp_target/wp_custom_directories'
require 'wp_target/wp_full_path_disclosure'

class WpTarget < WebSite
  include WpTarget::Malwares
  include WpTarget::WpReadme
  include WpTarget::WpRegistrable
  include WpTarget::WpConfigBackup
  include WpTarget::WpLoginProtection
  include WpTarget::WpCustomDirectories
  include WpTarget::WpFullPathDisclosure

  attr_reader :verbose

  def initialize(target_url, options = {})
    super(target_url)

    @verbose        = options[:verbose]
    @wp_content_dir = options[:wp_content_dir]
    @wp_plugins_dir = options[:wp_plugins_dir]
    @multisite      = nil
    @version_mappings = options[:version_mappings]

    Browser.instance(options.merge(:max_threads => options[:threads]))
  end

  def sharepoint?
    response = Browser.get_and_follow_location(@uri.to_s)
    has_sharepoint_headers?(response) || has_sharepoint_generator_tag?(response)
  end

  def login_url
    url = @uri.merge('wp-login.php').to_s

    # Let's check if the login url is redirected (to https url for example)
    redirection = redirection(url)
    if redirection
      url = redirection
    end

    url
  end

  # Valid HTTP return codes
  def self.valid_response_codes
    [200, 301, 302, 401, 403, 500, 400]
  end

  # @return [ WpTheme ]
  # :nocov:
  def theme
    WpTheme.find(@uri)
  end
  # :nocov:

  # @param [ String ] versions_xml
  #
  # @return [ WpVersion ]
  # :nocov:
  def version
    version_mappings.version_for version_header_value
  end
  # :nocov:

  # The version is not yet considerated
  #
  # @param [ String ] name
  # @param [ String ] version
  #
  # @return [ Boolean ]
  def has_plugin?(name, version = nil)
    WpPlugin.new(
      @uri,
      name: name,
      version: version,
      wp_content_dir: wp_content_dir,
      wp_plugins_dir: wp_plugins_dir
    ).exists?
  end

  # @return [ Boolean ]
  def has_debug_log?
    WebSite.has_log?(debug_log_url, %r{\[[^\]]+\] PHP (?:Warning|Error|Notice):})
  end

  def has_vulnerabilities?
    version.has_vulnerabilities?
  end

  # @return [ String ]
  def debug_log_url
    @uri.merge("#{wp_content_dir()}/debug.log").to_s
  end

  # Script for replacing strings in wordpress databases
  # reveals databse credentials after hitting submit
  # http://interconnectit.com/124/search-and-replace-for-wordpress-databases/
  #
  # @return [ String ]
  def search_replace_db_2_url
    @uri.merge('searchreplacedb2.php').to_s
  end

  # @return [ Boolean ]
  def search_replace_db_2_exists?
    resp = Browser.get(search_replace_db_2_url)
    resp.code == 200 && resp.body[%r{by interconnect}i]
  end

  def vulnerabilities
    version.vulnerabilities
  end

  private

    attr_reader :version_mappings

    def has_sharepoint_generator_tag?(response)
      html = Nokogiri::HTML.parse(response.response_body)
      html.search('meta[name="GENERATOR"][content="Microsoft SharePoint"]').any?
    end

    def has_sharepoint_headers?(response)
      response.headers and response.headers.keys.any? { |h| h.downcase == "MicrosoftSharePointTeamServices".downcase }
    end

    def version_header_value
      response = Browser.get_and_follow_location(@uri.to_s)
      response.headers and response.headers["MicrosoftSharePointTeamServices"]
    end
end
