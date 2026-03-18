import Foundation

protocol BackendURLStoring {
    func load() -> AppConfiguration
    func save(backendURLString: String) throws -> AppConfiguration
    func clear()
}

enum BackendURLStoreError: LocalizedError {
    case invalidURL

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Enter a valid http or https backend URL."
        }
    }
}

final class BackendURLStore: BackendURLStoring {
    private let userDefaults: UserDefaults
    private let backendURLKey = "listerine.backend-url"

    init(userDefaults: UserDefaults = .standard) {
        self.userDefaults = userDefaults
    }

    func load() -> AppConfiguration {
        guard
            let storedURL = userDefaults.string(forKey: backendURLKey),
            let url = URL(string: storedURL)
        else {
            return AppConfiguration(backendURL: nil)
        }

        return AppConfiguration(backendURL: url)
    }

    func save(backendURLString: String) throws -> AppConfiguration {
        let trimmedURL = backendURLString.trimmingCharacters(in: .whitespacesAndNewlines)

        guard
            let url = URL(string: trimmedURL),
            let scheme = url.scheme?.lowercased(),
            ["http", "https"].contains(scheme),
            url.host != nil
        else {
            throw BackendURLStoreError.invalidURL
        }

        userDefaults.set(url.absoluteString, forKey: backendURLKey)
        return AppConfiguration(backendURL: url)
    }

    func clear() {
        userDefaults.removeObject(forKey: backendURLKey)
    }
}
