require_relative '../../../lib/spscan/version_mappings'
require_relative '../../../lib/spscan/version'

module SpScan

  describe VersionMappings do

    it "returns an unknown version for an unknown header version" do
      mappings = VersionMappings.new({})
      unknown = mappings.version_for("unknown_header_value")
      unknown.should be_unknown
      unknown.to_s.should == "Unknown"
    end

    it "returns the version for a known header version" do
      expected_version = Object.new

      mappings = VersionMappings.new({"known_header_value" => expected_version})
      version = mappings.version_for "known_header_value"
      version.should == expected_version
    end
  end
end