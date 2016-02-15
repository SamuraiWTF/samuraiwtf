require_relative '../../../lib/spscan/version'

module SpScan

  describe Version do

    let(:version) { Version.new(identifier, vulnerability_source) }
    let(:identifier) { "foo" }
    let(:vulns) { [Object.new] }
    let(:vulnerability_source) {
      source = double("vulnerability source")
      source.stub(:vulnerabilities_for).and_return(vulns)
      source
    }

    it "returns the identifier for #to_s" do
      version.to_s.should == identifier
    end

    context "does not have vulnerabilities" do
      let(:vulnerability_source) {
        source = double("vulnerability source")
        source.stub(:vulnerabilities_for).and_return([])
        source
      }

      it "should not have vulnerabilities" do
        version.has_vulnerabilities?.should be_false
      end
    end

    context "does have vulnerabilities" do
      it "should have vulnerabilities" do
        version.has_vulnerabilities?.should be_true
      end
    end
  end
end