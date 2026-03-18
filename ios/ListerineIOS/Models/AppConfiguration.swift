import Foundation

struct AppConfiguration: Equatable {
    var backendURL: URL?

    var hasBackendURL: Bool {
        backendURL != nil
    }
}
