# encoding: UTF-8

require File.expand_path(File.dirname(__FILE__) + '/wpscan_helper')

describe WpTarget do
  subject(:wp_target) { WpTarget.new(target_url, options) }
  let(:target_url)    { 'http://example.localhost/' }
  let(:fixtures_dir)  { SPEC_FIXTURES_WPSCAN_WP_TARGET_DIR }
  let(:login_url)     { wp_target.uri.merge('wp-login.php').to_s }
  let(:options)       {
    {
      config_file:    SPEC_FIXTURES_CONF_DIR + '/browser/browser.conf.json',
      cache_ttl:      0,
      wp_content_dir: 'wp-content',
      wp_plugins_dir: 'wp-content/plugins'
    }
  }

  before { Browser::reset }

  it_behaves_like 'WpTarget::Malwares'
  it_behaves_like 'WpTarget::WpReadme'
  it_behaves_like 'WpTarget::WpRegistrable'
  it_behaves_like 'WpTarget::WpConfigBackup'
  it_behaves_like 'WpTarget::WpLoginProtection'
  it_behaves_like 'WpTarget::WpCustomDirectories'
  it_behaves_like 'WpTarget::WpFullPathDisclosure'

  describe '#initialize' do
    it 'should raise an error if the target_url is nil or empty' do
      expect { WpTarget.new(nil) }.to raise_error
      expect { Wptarget.new('') }.to raise_error
    end
  end

  describe '#login_url' do
    it 'returns the login url of the target' do
      stub_request(:get, login_url).to_return(status: 200, body: '')

      wp_target.login_url.should === login_url
    end

    it 'returns the redirection url if there is one (ie: for https)' do
      https_login_url = login_url.gsub(/^http:/, 'https:')

      stub_request(:get, login_url).to_return(status: 302, headers: { location: https_login_url })
      stub_request(:get, https_login_url).to_return(status: 200)

      wp_target.login_url.should === https_login_url
    end
  end

  describe '#sharepoint?' do

    context "not a SharePoint site" do

      it "is not a SharePoint site if no SharePoint specific headers or html content exist in the page." do
         stub_request_to_fixture(url: wp_target.url, fixture: fixtures_dir + '/wp_content_dir/not_sharepoint.html')

         wp_target.should_not be_sharepoint
      end

    end

    context "is a SharePoint site" do
      it "checks for a 'MicrosoftSharePointTeamServices' HTTP header" do
        stub_request(:get, wp_target.url).
          to_return(status: 200, body: '', headers: { "MicrosoftSharePointTeamServices" => "14.0.0.4762" })

        wp_target.should be_sharepoint
      end

      it "checks for a sharepoint GENERATOR meta tag" do
        stub_request_to_fixture(url: wp_target.url, fixture: fixtures_dir + '/wp_content_dir/sharepoint.html')

        wp_target.should be_sharepoint        
      end
    end

  end

  describe '#redirection' do
    it 'returns nil if no redirection detected' do
      stub_request(:get, wp_target.url).to_return(status: 200, body: '')

      wp_target.redirection.should be_nil
    end

    [301, 302].each do |status_code|
      it "returns http://new-location.com if the status code is #{status_code}" do
        new_location = 'http://new-location.com'

        stub_request(:get, wp_target.url).
          to_return(status: status_code, headers: { location: new_location })

        stub_request(:get, new_location).to_return(status: 200)

        wp_target.redirection.should === 'http://new-location.com'
      end
    end

    context 'when multiple redirections' do
      it 'returns the last redirection' do
        first_redirection  = 'www.redirection.com'
        last_redirection   = 'redirection.com'

        stub_request(:get, wp_target.url).to_return(status: 301, headers: { location: first_redirection })
        stub_request(:get, first_redirection).to_return(status: 302, headers: { location: last_redirection })
        stub_request(:get, last_redirection).to_return(status: 200)

        wp_target.redirection.should === last_redirection
      end
    end
  end

  describe '#debug_log_url' do
    it "returns 'http://example.localhost/wp-content/debug.log" do
      wp_target.stub(wp_content_dir: 'wp-content')
      wp_target.debug_log_url.should === 'http://example.localhost/wp-content/debug.log'
    end
  end

  describe '#has_debug_log?' do
    let(:fixtures_dir) { SPEC_FIXTURES_WPSCAN_WP_TARGET_DIR + '/debug_log' }

    after :each do
      wp_target.stub(wp_content_dir: 'wp-content')
      stub_request_to_fixture(url: wp_target.debug_log_url(), fixture: @fixture)
      wp_target.has_debug_log?.should === @expected
    end

    it 'returns false' do
      @fixture  = SPEC_FIXTURES_DIR + '/empty-file'
      @expected = false
    end

    it 'returns true' do
      @fixture  = fixtures_dir + '/debug.log'
      @expected = true
    end

    it 'should also detect it if there are PHP notice' do
      @fixture  = fixtures_dir + '/debug-notice.log'
      @expected = true
    end
  end

  describe '#search_replace_db_2_url' do
    it 'returns the correct url' do
      wp_target.search_replace_db_2_url.should == 'http://example.localhost/searchreplacedb2.php'
    end
  end

  describe '#search_replace_db_2_exists?' do
    it 'returns true' do
      stub_request(:any, wp_target.search_replace_db_2_url).to_return(status: 200, body: 'asdf by interconnect asdf')
      wp_target.search_replace_db_2_exists?.should be_true
    end

    it 'returns false' do
      stub_request(:any, wp_target.search_replace_db_2_url).to_return(status: 500)
      wp_target.search_replace_db_2_exists?.should be_false
    end

    it 'returns false' do
      stub_request(:any, wp_target.search_replace_db_2_url).to_return(status: 500, body: 'asdf by interconnect asdf')
      wp_target.search_replace_db_2_exists?.should be_false
    end
  end

  describe "version" do

      subject(:target) { WpTarget.new(target_url, options) }
      let(:expected_version) { "SPVERSION" }
      let(:target_url)    { 'http://example.localhost/' }
      let(:options) {
        version_mappings = double("version mappings")
        version_mappings.stub(:version_for).and_return(expected_version)
        {
          version_mappings: version_mappings  
        }        
      }

      it "returns an version number when the header not exists" do
        stub_request(:get, wp_target.url).
          to_return(status: 200, body: '', headers: { "MicrosoftSharePointTeamServices" => expected_version })

        target.version.should == expected_version
      end
  end

  describe "vulnerabilties" do

    subject(:target) { WpTarget.new(target_url, options) }

    let(:version_mappings) {
      mappings = double("version mappings")
      mappings.stub(:version_for).and_return(version)
      mappings
    }

    let(:options) {
      { version_mappings: version_mappings }  
    }

    context "when the current version has none" do

      let(:version) {
        version = double("version")
        version.stub(:has_vulnerabilities?).and_return(false)
        version
      }

      it "does not have vulnerabilties" do
        stub_request(:get, wp_target.url).
          to_return(status: 200, body: '', headers: { "MicrosoftSharePointTeamServices" => "14.0.0.4762" })

        target.has_vulnerabilities?.should be_false
      end

      context "when the current version has vulnerabilties" do

        let(:version) {
          version = double("version")
          version.stub(:has_vulnerabilities?).and_return(true)
          version
        }

        it "has vulnerabilties" do
          stub_request(:get, wp_target.url).
            to_return(status: 200, body: '', headers: { "MicrosoftSharePointTeamServices" => "14.0.0.4762" })

          target.has_vulnerabilities?.should be_true
        end

      end

    end
  end
end
