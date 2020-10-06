from django.urls import path
from rana.portfolio import views_portfolio

urlpatterns = [
    path('tags/portfolio', views_portfolio.TagInfo.as_view(), name='tags_portfolio'),
    path('tags/search', views_portfolio.TagSearch.as_view(), name='tags_Test'),
    path('tags', views_portfolio.TagInfo.as_view(), name='tags'),
    path('myportfolio', views_portfolio.PortfolioDetail.as_view(), name='myportfolio'),
    path('<portfolio_id>', views_portfolio.PortfolioInfo.as_view(), name='portfolio'),
    path('', views_portfolio.PortfolioList.as_view(), name='portfolios'),
]