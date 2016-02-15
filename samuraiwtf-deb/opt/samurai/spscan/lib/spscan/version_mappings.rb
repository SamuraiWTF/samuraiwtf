module SpScan
  class VersionMappings

    def initialize(mappings)
      @mappings = mappings
    end

    def version_for(header_value)
      mappings.fetch(header_value) { UnknownVersion.new }
    end

    private

    attr_reader :mappings

  end
end
