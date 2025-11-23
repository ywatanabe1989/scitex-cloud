/**
 * Notification Manager for Element Inspector
 * Handles notifications and visual effects
 */

export class NotificationManager {
  public showNotification(
    message: string,
    type: "success" | "error",
  ): void {
    const notification = document.createElement("div");
    notification.textContent = message;
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background: ${type === "success" ? "rgba(16, 185, 129, 0.95)" : "rgba(239, 68, 68, 0.95)"};
            color: white;
            border-radius: 6px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 14px;
            font-weight: bold;
            z-index: 10000000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease;
        `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = "slideOut 0.3s ease";
      setTimeout(() => notification.remove(), 300);
    }, 2000);
  }

  public showCameraFlash(): void {
    const flash = document.createElement("div");
    flash.className = "camera-flash";
    document.body.appendChild(flash);

    // Play camera shutter sound if available (optional)
    try {
      const audio = new Audio(
        "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuWkcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGnuTvuQ==",
      );
      audio.volume = 0.3;
      audio.play().catch(() => {
        // Ignore if audio play fails (autoplay policy)
      });
    } catch (e) {
      // Silently ignore audio errors
    }

    // Remove flash element after animation
    setTimeout(() => {
      flash.remove();
    }, 500);
  }
}
