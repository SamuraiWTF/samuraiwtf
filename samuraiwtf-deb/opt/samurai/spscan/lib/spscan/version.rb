module SpScan
  class Version

    attr_reader :identifier

    def initialize(identifier, vulnerability_source)
      @identifier = identifier
      @vulnerability_source = vulnerability_source
    end

    def has_vulnerabilities?
      vulnerabilities.any?
    end

    def to_s
      identifier
    end

    def unknown?
      false
    end

    def vulnerabilities
      vulnerability_source.vulnerabilities_for self
    end

    private

    attr_reader :vulnerability_source

  end

  class UnknownVersion
    def has_vulnerabilities?
      false
    end

    def unknown?
      true
    end

    def to_s
      "Unknown"
    end
  end
end
